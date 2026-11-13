from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

import agents
import auth
import db
import main
from conftest import AID, BID, COACH_A, COACH_B, make_jwt

ROUTES = [
    ("get", "/athletes", None),
    ("get", f"/athletes/{AID}/acwr", None),
    ("post", "/workouts", {"athlete_id": AID, "session_date": "2026-01-01", "duration_mins": 30, "rpe": 5}),
    ("delete", f"/athletes/{AID}/simulated-workouts", None),
    ("post", f"/athletes/{AID}/recovery-plan", None),
    ("post", "/coach-copilot", {"question": "who?"}),
    ("post", "/injury-chat", {"messages": [{"role": "user", "content": "knee"}]}),
    ("post", "/demo-roster", None),
]


def call(client, method, path, body=None, **kw):
    return getattr(client, method)(path, **({"json": body} if body is not None else {}), **kw)


@pytest.mark.parametrize("method,path,body", ROUTES)
def test_requests_without_a_token_are_401(anon_client, method, path, body):
    assert call(anon_client, method, path, body).status_code == 401


def test_food_analysis_needs_a_token_too(anon_client):
    r = anon_client.post("/food-analysis", data={"goal": "cut"}, files={"image": ("m.jpg", b"\xff\xd8\xff" + b"0" * 50, "image/jpeg")})
    assert r.status_code == 401


def test_bad_token_is_401(anon_client, monkeypatch):
    monkeypatch.setattr(auth, "_lookup", lambda token: None)  # well-formed but unknown to Supabase
    assert anon_client.get("/athletes", headers={"Authorization": f"Bearer {make_jwt()}"}).status_code == 401


def test_malformed_authorization_header_is_401(anon_client):
    assert anon_client.get("/athletes", headers={"Authorization": "Token abc"}).status_code == 401
    assert anon_client.get("/athletes", headers={"Authorization": "Bearer "}).status_code == 401


def test_junk_and_expired_tokens_never_reach_supabase(anon_client, monkeypatch):
    calls = []
    monkeypatch.setattr(auth, "_lookup", lambda token: calls.append(token) or COACH_A)
    for token in ("garbage", "a.b.c", make_jwt(expires_in=-10)):
        assert anon_client.get("/athletes", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    assert calls == []


def test_good_token_works_and_is_cached(anon_client, monkeypatch):
    calls = []
    monkeypatch.setattr(auth, "_lookup", lambda token: calls.append(token) or COACH_A)
    h = {"Authorization": f"Bearer {make_jwt()}"}
    assert anon_client.get("/athletes", headers=h).status_code == 200
    assert anon_client.get("/athletes", headers=h).status_code == 200
    assert len(calls) == 1


def test_cached_token_is_checked_again_after_the_ttl(anon_client, monkeypatch):
    calls = []
    monkeypatch.setattr(auth, "_lookup", lambda token: calls.append(token) or COACH_A)
    now = [5000.0]
    monkeypatch.setattr(auth.time, "monotonic", lambda: now[0])
    h = {"Authorization": f"Bearer {make_jwt()}"}
    anon_client.get("/athletes", headers=h)
    now[0] += auth.TOKEN_TTL_S + 1
    anon_client.get("/athletes", headers=h)
    assert len(calls) == 2


def test_token_cache_evicts_oldest_when_full(monkeypatch):
    monkeypatch.setattr(auth, "CACHE_MAX", 4)
    monkeypatch.setattr(auth, "_lookup", lambda token: "u")
    tokens = [make_jwt(expires_in=3600 + i) for i in range(6)]
    for t in tokens:
        auth.current_user(f"Bearer {t}")
    assert len(auth._token_cache) <= 4 and tokens[-1] in auth._token_cache


def test_lookup_maps_auth_errors_to_none_and_lets_network_errors_through(monkeypatch):
    from supabase_auth.errors import AuthApiError
    class FakeAuth:
        def __init__(self, exc): self.exc = exc
        def get_user(self, token): raise self.exc
    class FakeClient:
        def __init__(self, exc): self.auth = FakeAuth(exc)
    monkeypatch.setattr(db, "client", lambda: FakeClient(AuthApiError("bad", 401, "bad_jwt")))
    assert auth._lookup("t") is None
    import httpx
    monkeypatch.setattr(db, "client", lambda: FakeClient(httpx.ConnectError("down")))
    with pytest.raises(httpx.ConnectError):
        auth._lookup("t")


# ---- ownership: a coach only ever sees their own athletes ----
def test_athletes_lists_only_my_athletes(client, as_user):
    assert [a["id"] for a in client.get("/athletes").json()] == [AID]
    as_user(COACH_B)
    assert [a["id"] for a in client.get("/athletes").json()] == [BID]


@pytest.mark.parametrize("method,path,body", [
    ("get", f"/athletes/{BID}/acwr", None),
    ("post", "/workouts", {"athlete_id": BID, "session_date": "2026-01-01", "duration_mins": 30, "rpe": 5}),
    ("delete", f"/athletes/{BID}/simulated-workouts", None),
    ("post", f"/athletes/{BID}/recovery-plan", None),
])
def test_other_coachs_athlete_is_404(client, method, path, body):
    assert call(client, method, path, body).status_code == 404


def test_cross_coach_write_does_not_touch_data(client, store):
    before = len(store.logs)
    client.post("/workouts", json={"athlete_id": BID, "session_date": "2026-01-01", "duration_mins": 30, "rpe": 5})
    assert len(store.logs) == before


def test_copilot_only_sees_my_athletes(client, monkeypatch):
    seen = {}
    def fake(question, athletes):
        seen["names"] = [a["name"] for a in athletes]
        return "ok"
    monkeypatch.setattr(agents, "coach_answer", fake)
    assert client.post("/coach-copilot", json={"question": "who?"}).status_code == 200
    assert seen["names"] == ["Priya Nair"]


# ---- demo roster ----
def test_demo_roster_clones_templates_once(client, as_user, store):
    as_user("new-coach")
    assert client.post("/demo-roster").json() == {"created": 2}
    mine = client.get("/athletes").json()
    assert sorted(a["name"] for a in mine) == ["Template One", "Template Two"]
    assert all(a["id"] not in {"t1", "t2"} for a in mine)
    assert client.post("/demo-roster").json() == {"created": 0}
    assert len(client.get("/athletes").json()) == 2
    assert [a["id"] for a in store.athletes if a["coach_id"] is None] == ["t1", "t2"]  # templates untouched


def test_demo_roster_skipped_when_coach_already_has_athletes(client):
    assert client.post("/demo-roster").json() == {"created": 0}  # coach-a already owns Priya


def test_demo_roster_shifts_dates_so_acwr_matches_the_template(client, as_user, store):
    old = [dict(l, session_date=(date.fromisoformat(l["session_date"]) - timedelta(days=30)).isoformat())
           for l in store.logs if l["athlete_id"] in ("t1", "t2")]
    store.logs = [l for l in store.logs if l["athlete_id"] not in ("t1", "t2")] + old  # templates were seeded 30 days ago
    as_user("new-coach")
    client.post("/demo-roster")
    newest = max(l["session_date"] for l in store.logs if l["athlete_id"].startswith("new-coach-"))
    assert newest == date.today().isoformat()


def test_demo_roster_with_no_templates_creates_nothing(client, as_user, store):
    store.athletes = [a for a in store.athletes if a["coach_id"] is not None]
    as_user("new-coach")
    assert client.post("/demo-roster").json() == {"created": 0}


# ---- rate limiting ----
def test_ai_endpoint_is_limited_per_user(client, as_user, monkeypatch):
    monkeypatch.setitem(auth.LIMITS, "ai", 3)
    monkeypatch.setattr(agents, "coach_answer", lambda q, a: "ok")
    for _ in range(3):
        assert client.post("/coach-copilot", json={"question": "who?"}).status_code == 200
    r = client.post("/coach-copilot", json={"question": "who?"})
    assert r.status_code == 429 and "Retry-After" in r.headers
    as_user(COACH_B)  # a different user has their own budget
    assert client.post("/coach-copilot", json={"question": "who?"}).status_code == 200


def test_standard_endpoints_have_a_separate_budget(client, monkeypatch):
    monkeypatch.setitem(auth.LIMITS, "ai", 1)
    monkeypatch.setattr(agents, "coach_answer", lambda q, a: "ok")
    client.post("/coach-copilot", json={"question": "who?"})
    assert client.post("/coach-copilot", json={"question": "who?"}).status_code == 429
    assert client.get("/athletes").status_code == 200


def test_rate_limit_window_expires(client, monkeypatch):
    monkeypatch.setitem(auth.LIMITS, "std", 1)
    now = [1000.0]
    monkeypatch.setattr(auth.time, "monotonic", lambda: now[0])
    assert client.get("/athletes").status_code == 200
    assert client.get("/athletes").status_code == 429
    now[0] += 61
    assert client.get("/athletes").status_code == 200


def test_cors_preflight_allows_authorization_header(client):
    r = client.options("/athletes", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET",
                                             "Access-Control-Request-Headers": "authorization"})
    assert r.status_code == 200 and "authorization" in r.headers["access-control-allow-headers"].lower()


def test_health_is_public(anon_client):
    assert anon_client.get("/health").json() == {"status": "ok"}


def test_injury_chat_and_food_are_rate_limited_too(client, monkeypatch):
    monkeypatch.setitem(auth.LIMITS, "ai", 1)
    body = {"messages": [{"role": "user", "content": "knee"}]}
    monkeypatch.setattr(agents, "_chat_messages", lambda s, m: "Where?")
    assert client.post("/injury-chat", json=body).status_code == 200
    assert client.post("/injury-chat", json=body).status_code == 429


def test_programming_errors_are_500_not_masked_as_database_503(client, monkeypatch):
    def boom(*a):
        raise RuntimeError("a bug")
    monkeypatch.setattr(db, "list_athletes", boom)
    assert TestClient(main.app, raise_server_exceptions=False).get("/athletes").status_code == 500
