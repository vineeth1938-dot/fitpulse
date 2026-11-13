"""Supabase access. All queries go through here."""
import os
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv
from supabase import Client, create_client

from acwr import CHRONIC_DAYS

load_dotenv()

class DatabaseError(Exception):
    """The database is misconfigured or returned something unusable; the API answers 503."""


_client: Client | None = None


def client() -> Client:
    global _client
    if _client is None:
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise DatabaseError("SUPABASE_URL and SUPABASE_KEY must be set in backend/.env")
        _client = create_client(url, key)
    return _client


def list_athletes(coach_id: str) -> list[dict]:
    return client().table("athletes").select("*").eq("coach_id", coach_id).order("name").execute().data


def get_athlete(athlete_id: str, coach_id: str) -> dict | None:
    """Only returns the athlete if this coach owns it, so a guessed id from another coach looks like a 404."""
    rows = (client().table("athletes").select("*").eq("id", athlete_id).eq("coach_id", coach_id)
            .limit(1).execute().data)
    return rows[0] if rows else None


def logs_for(athlete_id: str, today: date) -> list[dict]:
    # trend needs a 28-day chronic window for each of the last 28 days
    since = (today - timedelta(days=2 * CHRONIC_DAYS)).isoformat()
    return (client().table("workout_logs").select("*").eq("athlete_id", athlete_id)
            .gte("session_date", since).execute().data)


PAGE = 1000  # PostgREST returns at most this many rows per request


def all_logs(today: date, athlete_ids: list[str]) -> list[dict]:
    if not athlete_ids:
        return []
    since = (today - timedelta(days=2 * CHRONIC_DAYS)).isoformat()
    rows: list[dict] = []
    while True:
        page = (client().table("workout_logs").select("*").in_("athlete_id", athlete_ids).gte("session_date", since)
                .order("id").range(len(rows), len(rows) + PAGE - 1).execute().data)
        rows += page
        if len(page) < PAGE:
            return rows


MAX_ATHLETES = 50  # per coach


def insert_athlete(coach_id: str, data: dict) -> dict:
    rows = client().table("athletes").insert({**data, "coach_id": coach_id}).execute().data
    if not rows:
        raise DatabaseError("Insert returned no row")
    return rows[0]


def delete_demo_athletes(coach_id: str) -> int:
    """Remove this coach's copies of the demo squad (their sessions go with them). Own athletes are kept."""
    rows = (client().table("athletes").delete().eq("coach_id", coach_id).not_.is_("template_id", "null")
            .execute().data)
    return len(rows)


SIMULATED_NOTE = "Simulated brutal practice"


def delete_simulated(athlete_id: str) -> None:
    client().table("workout_logs").delete().eq("athlete_id", athlete_id).eq("notes", SIMULATED_NOTE).execute()


def insert_workout(row: dict) -> dict:
    data = client().table("workout_logs").insert(row).execute().data
    if not data:
        raise DatabaseError("Insert returned no row")
    return data[0]


def clone_demo_roster(coach_id: str, today: date) -> int:
    """Give a coach their own copy of the demo squad in one database transaction (see db/migrations/001_auth.sql).
    Returns how many athletes the coach owns afterwards, or 0 if they already had some."""
    for attempt in (1, 2):
        try:
            data = client().rpc("clone_demo_roster", {"p_coach": coach_id, "p_today": today.isoformat()}).execute().data
            return int(data or 0)
        except httpx.TransportError:
            # A dropped connection. Safe to repeat: the function does nothing if the squad already exists, so if the
            # first attempt did work, the retry just returns 0.
            if attempt == 2:
                raise
    return 0
