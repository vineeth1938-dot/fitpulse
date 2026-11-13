"""Supabase access. All queries go through here."""
import os
from datetime import date, timedelta

from dotenv import load_dotenv
from supabase import Client, create_client

from acwr import CHRONIC_DAYS

load_dotenv()

_client: Client | None = None


def client() -> Client:
    global _client
    if _client is None:
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in backend/.env")
        _client = create_client(url, key)
    return _client


def list_athletes() -> list[dict]:
    return client().table("athletes").select("*").order("name").execute().data


def get_athlete(athlete_id: str) -> dict | None:
    rows = client().table("athletes").select("*").eq("id", athlete_id).limit(1).execute().data
    return rows[0] if rows else None


def logs_for(athlete_id: str, today: date) -> list[dict]:
    # trend needs a 28-day chronic window for each of the last 28 days
    since = (today - timedelta(days=2 * CHRONIC_DAYS)).isoformat()
    return (client().table("workout_logs").select("*").eq("athlete_id", athlete_id)
            .gte("session_date", since).execute().data)


def all_logs(today: date) -> list[dict]:
    since = (today - timedelta(days=2 * CHRONIC_DAYS)).isoformat()
    return client().table("workout_logs").select("*").gte("session_date", since).execute().data


SIMULATED_NOTE = "Simulated brutal practice"


def delete_simulated(athlete_id: str) -> None:
    client().table("workout_logs").delete().eq("athlete_id", athlete_id).eq("notes", SIMULATED_NOTE).execute()


def insert_workout(row: dict) -> dict:
    data = client().table("workout_logs").insert(row).execute().data
    if not data:
        raise RuntimeError("Insert returned no row")
    return data[0]
