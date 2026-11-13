
from datetime import date, timedelta

import pytest

from acwr import calculate_metrics, get_risk_status


def test_risk_status_categories():
    assert get_risk_status(0.50) == "Undertrained"
    assert get_risk_status(0.80) == "Safe"
    assert get_risk_status(1.30) == "Safe"
    assert get_risk_status(1.40) == "Caution"
    assert get_risk_status(1.60) == "Danger"


def test_calculate_metrics():
    today = date(2026, 11, 13)

    logs = [
        {
            "session_date": (today - timedelta(days=1)).isoformat(),
            "duration_mins": 40,
            "rpe": 5,
            "sleep_hours": 8.0
        },
        {
            "session_date": today.isoformat(),
            "duration_mins": 60,
            "rpe": 5,
            "sleep_hours": 7.5
        }
    ]

    result = calculate_metrics(logs, today=today)

    assert result["acute_load"] == pytest.approx(71.43)
    assert result["chronic_load"] == pytest.approx(17.86)
    assert result["acwr"] == 4.0
    assert result["risk_status"] == "Danger"
    assert result["latest_sleep_hours"] == 7.5
    assert len(result["trend"]) == 28


def test_empty_logs():
    result = calculate_metrics(
        [],
        today=date(2026, 11, 13)
    )

    assert result["acute_load"] == 0
    assert result["chronic_load"] == 0
    assert result["acwr"] == 0
    assert result["risk_status"] == "Undertrained"
    assert len(result["trend"]) == 28
