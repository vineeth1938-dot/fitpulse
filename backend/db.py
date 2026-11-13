
import os
from datetime import date, timedelta

from dotenv import load_dotenv
from supabase import create_client

# Load settings from the .env file
load_dotenv()

# Connect to Supabase only when needed
def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in backend/.env"
        )

    return create_client(url, key)


# Get all athletes
def list_athletes():
    response = (
        get_supabase()
        .table("athletes")
        .select("*")
        .execute()
    )
    return response.data


# Get one athlete by ID
def get_athlete(id):
    response = (
        get_supabase()
        .table("athletes")
        .select("*")
        .eq("id", id)
        .execute()
    )

    return response.data[0] if response.data else None


# Get workout logs from the last N calendar days
def get_logs(id, days=28):
    start_date = date.today() - timedelta(days=days - 1)

    response = (
        get_supabase()
        .table("workout_logs")
        .select("*")
        .eq("athlete_id", id)
        .gte("session_date", start_date.isoformat())
        .lte("session_date", date.today().isoformat())
        .order("session_date")
        .execute()
    )

    return response.data


# Get the newest N workouts
def get_recent_workouts(id, n=3):
    response = (
        get_supabase()
        .table("workout_logs")
        .select("*")
        .eq("athlete_id", id)
        .order("session_date", desc=True)
        .limit(n)
        .execute()
    )

    return response.data


# Insert a new workout
def insert_workout(data):
    response = (
        get_supabase()
        .table("workout_logs")
        .insert(data)
        .execute()
    )

    return response.data[0] if response.data else None
