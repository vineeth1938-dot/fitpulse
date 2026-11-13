import io

import pytest
from fastapi.testclient import TestClient

import agents
import coach
import main

JPEG = b"\xff\xd8\xff\xe0" + b"0" * 100
FOOD = {"foods": [{"name": "Rice", "calories": 200}, {"name": "Dal", "calories": 150}], "total_calories": 350,
        "protein_g": 14, "carbs_g": 60, "fat_g": 5, "goal_advice": "Eat protein.",
        "workout_plan": [{"activity": "Brisk walk", "minutes": 30, "calories_burned": 150}]}


@pytest.fixture
def client():
    return TestClient(main.app)


def post_food(client, data=JPEG, ctype="image/jpeg", goal="cut"):
    return client.post("/food-analysis", data={"goal": goal}, files={"image": ("meal.jpg", io.BytesIO(data), ctype)})


def test_food_analysis_returns_typed_result(client, monkeypatch):
    monkeypatch.setattr(coach, "_gemini_json", lambda *a, **k: FOOD)
    r = post_food(client)
    assert r.status_code == 200 and r.json()["total_calories"] == 350 and "disclaimer" in r.json()


def test_food_analysis_rejects_unknown_goal(client):
    assert post_food(client, goal="yolo").status_code == 422


def test_food_analysis_rejects_non_image_bytes(client):
    assert post_food(client, data=b"not an image at all", ctype="image/jpeg").status_code == 415


def test_food_analysis_rejects_oversize(client):
    assert post_food(client, data=JPEG + b"0" * (5 * 1024 * 1024)).status_code == 413


def test_food_analysis_ai_failure_is_502(client, monkeypatch):
    def boom(*a, **k):
        raise agents.AgentError("AI service unavailable")
    monkeypatch.setattr(coach, "_gemini_json", boom)
    assert post_food(client).status_code == 502


def test_food_analysis_malformed_ai_output_is_502(client, monkeypatch):
    monkeypatch.setattr(coach, "_gemini_json", lambda *a, **k: {"foods": "nope"})
    assert post_food(client).status_code == 502


def chat(client, msgs):
    return client.post("/injury-chat", json={"messages": msgs})


def test_injury_chat_asks_a_question_first(client, monkeypatch):
    monkeypatch.setattr(agents, "_chat_messages", lambda s, m: "Where exactly is the pain?")
    r = chat(client, [{"role": "user", "content": "my knee hurts"}]).json()
    assert r == {"reply": "Where exactly is the pain?", "questions_asked": 0, "done": False}


def test_injury_chat_advice_marker_ends_chat(client, monkeypatch):
    monkeypatch.setattr(agents, "_chat_messages", lambda s, m: "ADVICE: Try hip bridges.")
    r = chat(client, [{"role": "user", "content": "knee pain"}, {"role": "assistant", "content": "Where?"},
                      {"role": "user", "content": "front"}]).json()
    assert r["done"] and r["reply"] == "Try hip bridges."


def test_injury_chat_never_asks_a_sixth_question(client, monkeypatch):
    seen = {}
    def fake(system, msgs):
        seen["system"] = system
        return "One more question?"
    monkeypatch.setattr(agents, "_chat_messages", fake)
    msgs = []
    for i in range(5):
        msgs += [{"role": "user", "content": f"a{i}"}, {"role": "assistant", "content": f"q{i}?"}]
    msgs.append({"role": "user", "content": "last answer"})
    r = chat(client, msgs).json()
    assert r["done"] is True and "Do not ask any more questions" in seen["system"]


def test_injury_chat_validates_history(client):
    assert chat(client, []).status_code == 422
    assert chat(client, [{"role": "assistant", "content": "hi"}]).status_code == 422
    assert chat(client, [{"role": "system", "content": "x"}]).status_code == 422
    assert chat(client, [{"role": "user", "content": "x" * 1001}]).status_code == 422


def test_food_floats_are_rounded_not_rejected(client, monkeypatch):
    odd = {**FOOD, "protein_g": 23.5, "workout_plan": FOOD["workout_plan"] * 7}
    monkeypatch.setattr(coach, "_gemini_json", lambda *a, **k: odd)
    r = post_food(client)
    assert r.status_code == 200 and len(r.json()["workout_plan"]) == 5


def test_injury_chat_marker_variants_and_cap_fallback(client, monkeypatch):
    monkeypatch.setattr(agents, "_chat_messages", lambda s, m: "**ADVICE:** Try hip bridges.")
    r = chat(client, [{"role": "user", "content": "knee"}]).json()
    assert r["done"] and r["reply"] == "Try hip bridges."
    monkeypatch.setattr(agents, "_chat_messages", lambda s, m: "Another question?")
    msgs = []
    for i in range(5):
        msgs += [{"role": "user", "content": f"a{i}"}, {"role": "assistant", "content": f"q{i}?"}]
    r = chat(client, msgs + [{"role": "user", "content": "x"}]).json()
    assert r["done"] and r["reply"] == coach.CLOSING
