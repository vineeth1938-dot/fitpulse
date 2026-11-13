from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class WorkoutCreate(BaseModel):
	athlete_id: UUID
	session_date: date
	duration_mins: int = Field(gt=0)
	rpe: int = Field(ge=1, le=10)
	sleep_hours: float = Field(ge=0)
	notes: Optional[str] = None


class WorkoutResponse(BaseModel):
	athlete_id: str
	name: str
	sport: str
	acwr: float
	acute_load: float
	chronic_load: float
	risk_status: str
	latest_sleep_hours: Optional[float] = None
	trend: list[dict]


class AthleteResponse(BaseModel):
	athlete_id: str
	name: str
	sport: str
	acwr: float
	acute_load: float
	chronic_load: float
	risk_status: str


class ACWRResponse(BaseModel):
	acute_load: float
	chronic_load: float
	acwr: float
	risk_status: str
	trend: list[dict]
