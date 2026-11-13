from datetime import date, timedelta

import pytest

from acwr import compute_acwr, risk_status

TODAY = date(2026, 1, 31)


def log(days_ago, mins, rpe):
    return {"session_date": (TODAY - timedelta(days=days_ago)).isoformat(), "duration_mins": mins, "rpe": rpe}


def test_no_logs_gives_zero_and_undertraining():
    r = compute_acwr([], TODAY)
    assert (r["acute_load"], r["chronic_load"], r["acwr"]) == (0, 0, 0)
    assert r["risk_status"] == "Undertraining"


def test_rest_days_count_as_zero():
    # one 100-load session today: acute = 100/7, chronic = 100/28 -> ACWR 4.0
    r = compute_acwr([log(0, 10, 10)], TODAY)
    assert r["acute_load"] == pytest.approx(100 / 7, abs=0.05)
    assert r["chronic_load"] == pytest.approx(100 / 28, abs=0.05)
    assert r["acwr"] == 4.0


def test_multiple_sessions_same_day_are_summed():
    r = compute_acwr([log(0, 10, 5), log(0, 20, 5)], TODAY)
    assert r["acute_load"] == pytest.approx(150 / 7, abs=0.05)


def test_sessions_outside_28_days_ignored():
    r = compute_acwr([log(28, 60, 8)], TODAY)
    assert r["chronic_load"] == 0


@pytest.mark.parametrize(
    "value,expected",
    [(0.79, "Undertraining"), (0.80, "Safe"), (1.30, "Safe"), (1.31, "Caution"),
     (1.50, "Caution"), (1.51, "Danger"), (1.68, "Danger")],
)
def test_risk_bands(value, expected):
    assert risk_status(value) == expected


def test_trend_has_28_points_ending_today():
    r = compute_acwr([log(20, 60, 6), log(3, 60, 6)], TODAY)
    assert len(r["trend"]) == 28
    assert r["trend"][-1]["date"] == TODAY.isoformat()
    assert r["trend"][0]["date"] == (TODAY - timedelta(days=27)).isoformat()
    assert r["trend"][-1]["acwr"] == r["acwr"]


def test_trend_acwr_is_null_during_warmup():
    r = compute_acwr([log(20, 60, 6), log(0, 60, 6)], TODAY)
    by_date = {p["date"]: p["acwr"] for p in r["trend"]}
    assert by_date[(TODAY - timedelta(days=20)).isoformat()] is None
    assert by_date[(TODAY - timedelta(days=7)).isoformat()] is not None
