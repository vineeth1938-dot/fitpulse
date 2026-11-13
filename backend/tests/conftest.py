"""Shared fixtures: an in-memory stand-in for db.py that enforces coach ownership, plus auth overrides."""
from datetime import date, timedelta

import base64
from uuid import uuid4
import json
import time

import pytest
from fastapi.testclient import TestClient

import auth
import db
import main

AID = "22222222-2222-2222-2222-222222222222"   # Priya, owned by coach-a
BID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"   # owned by coach-b
COACH_A, COACH_B = "coach-a", "coach-b"


def make_jwt(expires_in: int = 3600) -> str:
    """A structurally valid token (signature is junk): what the local pre-check accepts. Supabase would verify it for real."""
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
    return f"{enc({'alg': 'HS256'})}.{enc({'sub': 'u', 'exp': time.time() + expires_in})}.sig"


def _logs(athlete_id: str, shift: int = 0) -> list[dict]:
    return [{"athlete_id": athlete_id, "session_date": (date.today() - timedelta(days=i + shift)).isoformat(),
             "duration_mins": 60, "rpe": 6, "sleep_hours": 8.0, "notes": "x"} for i in range(0, 28, 2)]


class FakeDB:
    def __init__(self) -> None:
        self.athletes = [
            {"id": AID, "name": "Priya Nair", "sport": "Football", "position": "Midfielder", "coach_id": COACH_A, "template_id": None},
            {"id": BID, "name": "Bella B", "sport": "Rugby", "position": "Wing", "coach_id": COACH_B, "template_id": None},
            {"id": "t1", "name": "Template One", "sport": "Cricket", "position": "Bowler", "coach_id": None, "template_id": None},
            {"id": "t2", "name": "Template Two", "sport": "Hockey", "position": "Mid", "coach_id": None, "template_id": None},
        ]
        self.logs = _logs(AID) + _logs(BID) + _logs("t1", 0) + _logs("t2", 0)

    def list_athletes(self, coach_id):
        return sorted((a for a in self.athletes if a["coach_id"] == coach_id), key=lambda a: a["name"])

    def get_athlete(self, athlete_id, coach_id):
        return next((a for a in self.athletes if a["id"] == athlete_id and a["coach_id"] == coach_id), None)

    def all_logs(self, today, athlete_ids):
        return [l for l in self.logs if l["athlete_id"] in athlete_ids]

    def logs_for(self, athlete_id, today):
        return [l for l in self.logs if l["athlete_id"] == athlete_id]

    def insert_workout(self, row):
        self.logs.append(row)
        return row

    def delete_simulated(self, athlete_id):
        self.logs = [l for l in self.logs if not (l["athlete_id"] == athlete_id and l.get("notes") == db.SIMULATED_NOTE)]

    def insert_athlete(self, coach_id, data):
        row = {"id": str(uuid4()), "sport": None, "position": None, "resting_hr": None, **data,
               "coach_id": coach_id, "template_id": None}
        self.athletes.append(row)
        return row

    def delete_demo_athletes(self, coach_id):
        gone = {a["id"] for a in self.athletes if a["coach_id"] == coach_id and a["template_id"]}
        self.athletes = [a for a in self.athletes if a["id"] not in gone]
        self.logs = [l for l in self.logs if l["athlete_id"] not in gone]  # the real database cascades
        return len(gone)

    def clone_demo_roster(self, coach_id, today):
        if any(a["coach_id"] == coach_id and a["template_id"] for a in self.athletes):
            return 0  # the real unique index makes a second clone fail
        templates = [a for a in self.athletes if a["coach_id"] is None]
        if not templates:
            return 0
        tlogs = [l for l in self.logs if l["athlete_id"] in {t["id"] for t in templates}]
        shift = today - max(date.fromisoformat(l["session_date"]) for l in tlogs)  # same rule as the SQL function
        for i, t in enumerate(templates):
            new_id = f"{coach_id}-{t['id']}"
            self.athletes.append({**t, "id": new_id, "coach_id": coach_id, "template_id": t["id"]})
            self.logs += [{**l, "athlete_id": new_id, "session_date": (date.fromisoformat(l["session_date"]) + shift).isoformat()}
                          for l in tlogs if l["athlete_id"] == t["id"]]
        return len(templates)


@pytest.fixture
def store(monkeypatch):
    fake = FakeDB()
    for name in ("list_athletes", "get_athlete", "all_logs", "logs_for", "insert_workout", "delete_simulated", "clone_demo_roster", "insert_athlete", "delete_demo_athletes"):
        monkeypatch.setattr(db, name, getattr(fake, name))
    auth.reset_state()
    yield fake
    main.app.dependency_overrides.clear()
    auth.reset_state()


@pytest.fixture
def as_user(store):
    def _set(user_id: str):
        main.app.dependency_overrides[auth.current_user] = lambda: user_id
    return _set


@pytest.fixture
def client(store, as_user):
    as_user(COACH_A)
    return TestClient(main.app)


@pytest.fixture
def anon_client(store):
    """No dependency override: the real token check runs."""
    return TestClient(main.app)
