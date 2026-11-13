from datetime import date

import httpx
import pytest

import db


class FakeRpc:
    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.calls = 0

    def rpc(self, name, params):
        assert name == "clone_demo_roster" and set(params) == {"p_coach", "p_today"}
        return self

    def execute(self):
        self.calls += 1
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return type("R", (), {"data": out})()


@pytest.fixture
def fake(monkeypatch):
    def make(outcomes):
        f = FakeRpc(outcomes)
        monkeypatch.setattr(db, "client", lambda: f)
        return f
    return make


def test_clone_retries_once_after_a_dropped_connection(fake):
    f = fake([httpx.RemoteProtocolError("Server disconnected"), 10])
    assert db.clone_demo_roster("u", date(2026, 1, 1)) == 10 and f.calls == 2


def test_clone_gives_up_after_two_dropped_connections(fake):
    f = fake([httpx.RemoteProtocolError("a"), httpx.ConnectError("b")])
    with pytest.raises(httpx.TransportError):
        db.clone_demo_roster("u", date(2026, 1, 1))
    assert f.calls == 2


def test_clone_does_not_retry_other_errors(fake):
    f = fake([ValueError("bad"), 10])
    with pytest.raises(ValueError):
        db.clone_demo_roster("u", date(2026, 1, 1))
    assert f.calls == 1


def test_clone_returns_zero_when_the_squad_already_exists(fake):
    fake([httpx.RemoteProtocolError("response lost, but the first attempt had worked"), 0])
    assert db.clone_demo_roster("u", date(2026, 1, 1)) == 0
