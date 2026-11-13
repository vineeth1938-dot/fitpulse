"""ACWR engine. Pure functions, no I/O.

Session load = duration_mins * rpe. Daily load = sum of that day's sessions
(rest days = 0). Acute = mean daily load over 7 days, chronic = over 28 days.
"""
from collections import defaultdict
from datetime import date, timedelta

ACUTE_DAYS = 7
CHRONIC_DAYS = 28
SAFE_MIN, SAFE_MAX, CAUTION_MAX = 0.80, 1.30, 1.50
WARMUP_DAYS = 14  # trend points with less history than this are null (ratio is meaningless)


def risk_status(acwr: float) -> str:
    if acwr < SAFE_MIN:
        return "Undertraining"
    if acwr <= SAFE_MAX:
        return "Safe"
    if acwr <= CAUTION_MAX:
        return "Caution"
    return "Danger"


def _daily_loads(logs: list[dict]) -> dict[date, int]:
    loads: dict[date, int] = defaultdict(int)
    for row in logs:
        loads[date.fromisoformat(str(row["session_date"]))] += row["duration_mins"] * row["rpe"]
    return loads


def _window_mean(loads: dict[date, int], end: date, days: int) -> float:
    return sum(loads.get(end - timedelta(days=i), 0) for i in range(days)) / days


def _ratio(acute: float, chronic: float) -> float:
    return round(acute / chronic, 2) if chronic > 0 else 0.0


def compute_acwr(logs: list[dict], today: date) -> dict:
    loads = _daily_loads(logs)
    first = min(loads) if loads else None
    trend = []
    for offset in range(CHRONIC_DAYS - 1, -1, -1):
        day = today - timedelta(days=offset)
        acute = _window_mean(loads, day, ACUTE_DAYS)
        chronic = _window_mean(loads, day, CHRONIC_DAYS)
        warmed = first is not None and (day - first).days >= WARMUP_DAYS - 1
        trend.append({"date": day.isoformat(), "acute_load": round(acute, 1),
                      "chronic_load": round(chronic, 1), "acwr": _ratio(acute, chronic) if warmed else None})
    acute = _window_mean(loads, today, ACUTE_DAYS)
    chronic = _window_mean(loads, today, CHRONIC_DAYS)
    ratio = _ratio(acute, chronic)
    return {"acute_load": round(acute, 1), "chronic_load": round(chronic, 1),
            "acwr": ratio, "risk_status": risk_status(ratio), "trend": trend}
