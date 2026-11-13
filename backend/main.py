"""FitPulse API. Run: uvicorn main:app --port 8000"""
import logging
import os
from datetime import date
from uuid import UUID

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import agents
import db
from acwr import compute_acwr

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


@app.get("/athletes")
def athletes():
    return _all_summaries()


@app.get("/athletes/{athlete_id}/acwr")
def athlete_acwr(athlete_id: UUID):
    _athlete_or_404(athlete_id)
    return compute_acwr(db.logs_for(str(athlete_id), date.today()), date.today())


@app.post("/workouts", status_code=201)
def add_workout(w: WorkoutIn):
    _athlete_or_404(w.athlete_id)
    db.insert_workout(w.model_dump(mode="json"))
    return compute_acwr(db.logs_for(str(w.athlete_id), date.today()), date.today())


@app.delete("/athletes/{athlete_id}/simulated-workouts")
def reset_demo(athlete_id: UUID):
    _athlete_or_404(athlete_id)
    db.delete_simulated(str(athlete_id))
    return compute_acwr(db.logs_for(str(athlete_id), date.today()), date.today())


@app.post("/athletes/{athlete_id}/recovery-plan")
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


@app.post("/coach-copilot")
def coach_copilot(q: QuestionIn):
    try:
        return {"answer": agents.coach_answer(q.question, _all_summaries())}
    except agents.AgentError as exc:
        raise HTTPException(502, str(exc)) from exc
