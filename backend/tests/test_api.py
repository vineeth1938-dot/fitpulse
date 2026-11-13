from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import db
import main

AID = "22222222-2222-2222-2222-222222222222"
ATHLETE = {"id": AID, "name": "Priya Nair", "sport": "Football", "position": "Midfielder"}


@pytest.fixture
def client(monkeypatch):
    logs = [{"athlete_id": AID, "session_date": (date.today() - timedelta(days=i)).isoformat(),
             "duration_mins": 60, "rpe": 6, "sleep_hours": 8.0} for i in range(0, 28, 2)]
    monkeypatch.setattr(db, "list_athletes", lambda: [ATHLETE])
    monkeypatch.setattr(db, "get_athlete", lambda i: ATHLETE if i == AID else None)
    monkeypatch.setattr(db, "all_logs", lambda t: logs)
    monkeypatch.setattr(db, "logs_for", lambda i, t: logs)
    monkeypatch.setattr(db, "insert_workout", lambda row: row)
    return TestClient(main.app)


def test_athletes_include_acwr(client):
    body = client.get("/athletes").json()
    assert body[0]["name"] == "Priya Nair" and body[0]["risk_status"] in {"Safe", "Caution", "Danger", "Undertraining"}


def test_acwr_has_28_day_trend(client):
    assert len(client.get(f"/athletes/{AID}/acwr").json()["trend"]) == 28


def test_unknown_athlete_404(client):
    assert client.get("/athletes/99999999-9999-9999-9999-999999999999/acwr").status_code == 404


def test_workout_validation_rejects_bad_rpe(client):
    r = client.post("/workouts", json={"athlete_id": AID, "session_date": "2026-01-01", "duration_mins": 30, "rpe": 11})
    assert r.status_code == 422


def test_workout_returns_recalculated_acwr(client):
    r = client.post("/workouts", json={"athlete_id": AID, "session_date": date.today().isoformat(),
                                       "duration_mins": 30, "rpe": 5})
    assert r.status_code == 201 and "acwr" in r.json()


def test_ai_failure_is_502_not_500(client, monkeypatch):
    def boom(*a, **k):
        raise main.agents.AgentError("AI service unavailable")
    monkeypatch.setattr(main.agents, "coach_answer", boom)
    assert client.post("/coach-copilot", json={"question": "who is at risk?"}).status_code == 502


def test_parse_plan_clamps_and_requires_three_drills():
    from agents import AgentError, _parse_plan
    ok = _parse_plan('x {"risk_summary":"a","deload_percentage":90,"mobility_drills":["a","b","c"],"nutrition_hydration_tip":"t"} y')
    assert ok["deload_percentage"] == 50
    with pytest.raises(AgentError):
        _parse_plan('{"risk_summary":"a","deload_percentage":10,"mobility_drills":["a"],"nutrition_hydration_tip":"t"}')


def test_reset_simulated_workouts_returns_fresh_acwr(client, monkeypatch):
    deleted = []
    monkeypatch.setattr(db, "delete_simulated", lambda i: deleted.append(i))
    r = client.delete(f"/athletes/{AID}/simulated-workouts")
    assert r.status_code == 200 and deleted == [AID] and "acwr" in r.json()


def test_reset_unknown_athlete_404(client):
    assert client.delete("/athletes/99999999-9999-9999-9999-999999999999/simulated-workouts").status_code == 404


def test_database_failure_is_503_not_500(client, monkeypatch):
    def boom():
        raise RuntimeError("db down")
    monkeypatch.setattr(db, "list_athletes", boom)
    assert TestClient(main.app, raise_server_exceptions=False).get("/athletes").status_code == 503


def test_parse_plan_rejects_string_drills_and_infinity():
    from agents import AgentError, _parse_plan
    for bad in ('{"risk_summary":"a","deload_percentage":10,"mobility_drills":"abc","nutrition_hydration_tip":"t"}',
                '{"risk_summary":"a","deload_percentage":Infinity,"mobility_drills":["a","b","c"],"nutrition_hydration_tip":"t"}'):
        with pytest.raises(AgentError):
            _parse_plan(bad)
