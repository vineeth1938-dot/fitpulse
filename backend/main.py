
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from db import insert_workout
from acwr import get_athlete_metrics, list_athlete_metrics
from schemas import WorkoutCreate


app = FastAPI(
    title="FitPulse API",
    description="Athlete workload and injury-risk monitoring",
    version="1.0.0"
)


# Allow our frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Welcome to FitPulse API!"}


# Get all athletes with their workload metrics.
@app.get("/athletes")
def get_athletes():
    try:
        athletes = list_athlete_metrics()

        return [
            {
                "athlete_id": athlete["athlete_id"],
                "name": athlete["name"],
                "sport": athlete["sport"],
                "acwr": athlete["acwr"],
                "acute_load": athlete["acute_load"],
                "chronic_load": athlete["chronic_load"],
                "risk_status": athlete["risk_status"]
            }
            for athlete in athletes
        ]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve athletes. Check database connection."
        ) from error


# Get ACWR details for one athlete.
@app.get("/athletes/{id}/acwr")
def get_acwr(id: str):
    try:
        metrics = get_athlete_metrics(id)

        return {
            "acute_load": metrics["acute_load"],
            "chronic_load": metrics["chronic_load"],
            "acwr": metrics["acwr"],
            "risk_status": metrics["risk_status"],
            "trend": metrics["trend"]
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Could not calculate ACWR. Check database connection."
        ) from error


# Add a new workout and return recalculated metrics.
@app.post("/workouts")
def create_workout(workout: WorkoutCreate):
    try:
        workout_data = workout.model_dump(mode="json")

        inserted_workout = insert_workout(workout_data)

        if inserted_workout is None:
            raise HTTPException(
                status_code=500,
                detail="Workout could not be saved"
            )

        return get_athlete_metrics(str(workout.athlete_id))

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail="Athlete not found"
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Could not save workout. Check database connection."
        ) from error
