import pytest

import agents


class _Choice:
    def __init__(self, content, finish):
        self.message = type("M", (), {"content": content})()
        self.finish_reason = finish


class FakeSarvam:
    """Replays queued replies and records the max_tokens of each call."""
    replies: list = []
    budgets: list = []

    def __init__(self, api_subscription_key):
        pass

    @property
    def chat(self):
        return self

    def completions(self, **kw):
        FakeSarvam.budgets.append(kw["max_tokens"])
        item = FakeSarvam.replies.pop(0)
        if isinstance(item, Exception):
            raise item
        content, finish = item
        return type("R", (), {"choices": [_Choice(content, finish)]})()


@pytest.fixture
def sarvam(monkeypatch):
    FakeSarvam.replies, FakeSarvam.budgets = [], []
    monkeypatch.setattr(agents, "SarvamAI", FakeSarvam)
    monkeypatch.setenv("SARVAM_API_KEY", "test")
    return FakeSarvam


def test_retries_with_a_bigger_budget_when_the_model_runs_out_of_tokens(sarvam):
    sarvam.replies = [(None, "length"), ("hello", "stop")]
    assert agents._chat("sys", "hi") == "hello"
    assert len(sarvam.budgets) == 2 and sarvam.budgets[1] > sarvam.budgets[0]


def test_first_budget_is_large_enough_for_thinking(sarvam):
    sarvam.replies = [("ok", "stop")]
    agents._chat("sys", "hi")
    assert sarvam.budgets[0] >= 8000


def test_gives_up_cleanly_if_even_the_bigger_budget_runs_out(sarvam):
    sarvam.replies = [(None, "length"), (None, "length")]
    with pytest.raises(agents.AgentError, match="empty"):
        agents._chat("sys", "hi")


def test_does_not_retry_when_empty_for_another_reason(sarvam):
    sarvam.replies = [(None, "stop")]
    with pytest.raises(agents.AgentError):
        agents._chat("sys", "hi")
    assert len(sarvam.budgets) == 1


def test_retries_once_when_the_request_hangs_or_fails(sarvam):
    sarvam.replies = [TimeoutError("hung"), ("hello", "stop")]
    assert agents._chat("sys", "hi") == "hello"
    assert sarvam.budgets == [8000, 8000]  # same budget: the failure was not about size


def test_gives_up_after_a_second_failure(sarvam):
    sarvam.replies = [TimeoutError("hung"), TimeoutError("hung again")]
    with pytest.raises(agents.AgentError, match="unavailable"):
        agents._chat("sys", "hi")
    assert len(sarvam.budgets) == 2


def test_a_hung_request_is_cut_off_well_before_two_minutes():
    assert agents.REQUEST_TIMEOUT_S <= 90
