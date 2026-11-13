"""FitPulse API. Run: uvicorn main:app --port 8000"""
import logging
import os
from datetime import date
from typing import Literal
from uuid import UUID

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

import agents
import coach
import db
from acwr import compute_acwr
from schemas import AcwrDetail, AthleteOut, CopilotOut, InjuryChatOut, RecoveryPlanOut

log = logging.getLogger("fitpulse")
app = FastAPI(title="FitPulse")
app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()],
                   allow_methods=["GET", "POST", "DELETE"], allow_headers=["Content-Type"])


@app.exception_handler(APIError)
@app.exception_handler(httpx.HTTPError)
@app.exception_handler(RuntimeError)
async def database_unavailable(request: Request, exc: Exception):
    log.exception("Database call failed on %s", request.url.path)
    return JSONResponse({"detail": "Database unavailable"}, status_code=503)


class WorkoutIn(BaseModel):
    athlete_id: UUID
    session_date: date
    duration_mins: int = Field(gt=0, le=600)
    rpe: int = Field(ge=1, le=10)
    sleep_hours: float | None = Field(default=None, ge=0, le=24)
    notes: str | None = Field(default=None, max_length=500)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)


class InjuryChatIn(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=20)


class QuestionIn(BaseModel):
    question: str = Field(min_length=1, max_length=500)


def _athlete_or_404(athlete_id: UUID) -> dict:
    athlete = db.get_athlete(str(athlete_id))
    if not athlete:
        raise HTTPException(404, "Athlete not found")
    return athlete


def _summary(logs: list[dict]) -> dict:
    result = compute_acwr(logs, date.today())
    return {k: result[k] for k in ("acute_load", "chronic_load", "acwr", "risk_status")}


def _all_summaries() -> list[dict]:
    logs = db.all_logs(date.today())
    return [{**a, **_summary([l for l in logs if l["athlete_id"] == a["id"]])} for a in db.list_athletes()]


@app.get("/athletes", response_model=list[AthleteOut])
def athletes():
    return _all_summaries()


@app.get("/athletes/{athlete_id}/acwr", response_model=AcwrDetail)
def athlete_acwr(athlete_id: UUID):
    _athlete_or_404(athlete_id)
    return compute_acwr(db.logs_for(str(athlete_id), date.today()), date.today())


@app.post("/workouts", status_code=201, response_model=AcwrDetail)
def add_workout(w: WorkoutIn):
    _athlete_or_404(w.athlete_id)
    db.insert_workout(w.model_dump(mode="json"))
    return compute_acwr(db.logs_for(str(w.athlete_id), date.today()), date.today())


@app.delete("/athletes/{athlete_id}/simulated-workouts", response_model=AcwrDetail)
def reset_demo(athlete_id: UUID):
    _athlete_or_404(athlete_id)
    db.delete_simulated(str(athlete_id))
    return compute_acwr(db.logs_for(str(athlete_id), date.today()), date.today())


@app.post("/athletes/{athlete_id}/recovery-plan", response_model=RecoveryPlanOut)
def recovery_plan(athlete_id: UUID):
    athlete = _athlete_or_404(athlete_id)
    logs = db.logs_for(str(athlete_id), date.today())
    sleeps = [l["sleep_hours"] for l in sorted(logs, key=lambda l: l["session_date"])[-5:]
              if l.get("sleep_hours") is not None]
    sleep = round(sum(sleeps) / len(sleeps), 1) if sleeps else None
    try:
        return agents.recovery_plan(athlete, _summary(logs), sleep)
    except agents.AgentError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.post("/coach-copilot", response_model=CopilotOut)
def coach_copilot(q: QuestionIn):
    try:
        return {"answer": agents.coach_answer(q.question, _all_summaries())}
    except agents.AgentError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.post("/food-analysis", response_model=coach.FoodAnalysis)
async def food_analysis(image: UploadFile = File(...), goal: Literal["slim", "cut", "bulk", "healthy"] = Form(...)):
    data = await image.read(coach.MAX_IMAGE_BYTES + 1)
    if len(data) > coach.MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image must be under 5 MB")
    if not coach.is_image(data):
        raise HTTPException(415, "Upload a JPEG, PNG or WebP image")
    try:
        return await run_in_threadpool(coach.analyze_food, data, goal)  # blocking Gemini call: keep the event loop free
    except agents.AgentError as exc:
        raise HTTPException(502, str(exc)) from exc


@app.post("/injury-chat", response_model=InjuryChatOut)
def injury_chat(body: InjuryChatIn):
    msgs = [m.model_dump() for m in body.messages]
    if msgs[-1]["role"] != "user":
        raise HTTPException(422, "The last message must be from the user")
    try:
        return coach.injury_chat(msgs)
    except agents.AgentError as exc:
        raise HTTPException(502, str(exc)) from exc
