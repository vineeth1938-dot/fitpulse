import pytest

import auth
import db
from conftest import AID, BID, COACH_A, COACH_B

NEW = {"name": "  Vineeth  ", "sport": "Cricket", "position": "Batter", "resting_hr": 60}


def test_add_athlete_creates_one_owned_by_me(client, as_user):
    r = client.post("/athletes", json=NEW)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Vineeth" and body["is_demo"] is False and "coach_id" not in body
    assert body["acwr"] == 0 and body["risk_status"] == "Undertraining"
    assert body["id"] in [a["id"] for a in client.get("/athletes").json()]
    as_user(COACH_B)
    assert body["id"] not in [a["id"] for a in client.get("/athletes").json()]


def test_new_athlete_can_log_sessions(client):
    new = client.post("/athletes", json=NEW).json()
    r = client.post("/workouts", json={"athlete_id": new["id"], "session_date": "2026-11-13", "duration_mins": 40, "rpe": 6})
    assert r.status_code == 201


@pytest.mark.parametrize("bad", [
    {"name": ""}, {"name": "   "}, {"name": "x" * 61}, {"name": "A", "resting_hr": 300}, {"name": "A", "resting_hr": 5},
    {"name": "A", "sport": "s" * 41}, {},
])
def test_add_athlete_validates_input(client, bad):
    assert client.post("/athletes", json=bad).status_code == 422


def test_name_only_is_enough(client):
    assert client.post("/athletes", json={"name": "Solo"}).status_code == 201


def test_athlete_count_is_capped(client, store, monkeypatch):
    monkeypatch.setattr(db, "MAX_ATHLETES", 2)  # coach-a already owns 1
    assert client.post("/athletes", json={"name": "Two"}).status_code == 201
    assert client.post("/athletes", json={"name": "Three"}).status_code == 400


def test_add_athlete_needs_a_login(anon_client):
    assert anon_client.post("/athletes", json=NEW).status_code == 401


def test_demo_copies_are_flagged(client, as_user):
    as_user("new-coach")
    client.post("/demo-roster")
    mine = client.get("/athletes").json()
    assert mine and all(a["is_demo"] for a in mine)
    client.post("/athletes", json={"name": "Me"})
    flags = {a["name"]: a["is_demo"] for a in client.get("/athletes").json()}
    assert flags["Me"] is False and flags["Template One"] is True


def test_remove_demo_athletes_keeps_my_own_and_others(client, as_user, store):
    as_user("new-coach")
    client.post("/demo-roster")
    client.post("/athletes", json={"name": "Me"})
    r = client.delete("/demo-athletes")
    assert r.json() == {"deleted": 2}
    assert [a["name"] for a in client.get("/athletes").json()] == ["Me"]
    as_user(COACH_A)  # someone else's data is untouched
    assert [a["id"] for a in client.get("/athletes").json()] == [AID]
    as_user(COACH_B)
    assert [a["id"] for a in client.get("/athletes").json()] == [BID]
    assert [a["id"] for a in store.athletes if a["coach_id"] is None] == ["t1", "t2"]  # templates too


def test_remove_demo_athletes_twice_is_harmless(client, as_user):
    as_user("new-coach")
    client.post("/demo-roster")
    client.delete("/demo-athletes")
    assert client.delete("/demo-athletes").json() == {"deleted": 0}


def test_remove_demo_athletes_needs_a_login(anon_client):
    assert anon_client.delete("/demo-athletes").status_code == 401
