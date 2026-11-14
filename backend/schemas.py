"""Response models: they document the API in /docs and stop stray fields leaking out."""
from typing import Literal

from pydantic import BaseModel

Risk = Literal["Safe", "Caution", "Danger", "Undertraining"]


class TrendPoint(BaseModel):
    date: str
    acute_load: float
    chronic_load: float
    acwr: float | None  # null while the athlete has under 14 days of history


class AcwrSummary(BaseModel):
    acute_load: float
    chronic_load: float
    acwr: float
    risk_status: Risk


class AcwrDetail(AcwrSummary):
    trend: list[TrendPoint]


class AthleteOut(AcwrSummary):
    id: str
    is_demo: bool = False  # a copy of the demo squad, removable in one click
    name: str
    sport: str | None = None
    position: str | None = None
    resting_hr: int | None = None


class RecoveryPlanOut(BaseModel):
    risk_summary: str
    deload_percentage: int
    mobility_drills: list[str]
    nutrition_hydration_tip: str


class CopilotOut(BaseModel):
    answer: str


class InjuryChatOut(BaseModel):
    reply: str
    questions_asked: int
    done: bool


class DemoRosterOut(BaseModel):
    created: int


class DeletedOut(BaseModel):
    deleted: int
