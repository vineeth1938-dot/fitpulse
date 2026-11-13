from datetime import date, timedelta

from db import get_athlete, get_logs, list_athletes


def get_risk_status(acwr):
	"""Convert ACWR number into a risk category."""
	if acwr < 0.80:
		return "Undertrained"
	elif acwr <= 1.30:
		return "Safe"
	elif acwr <= 1.50:
		return "Caution"
	else:
		return "Danger"


def calculate_metrics(logs, today=None):
	"""Calculate daily loads, acute load, chronic load and ACWR."""
	if today is None:
		today = date.today()

	window_start = today - timedelta(days=27)

	# Create 28 calendar days, including rest days.
	daily_loads = {
		window_start + timedelta(days=i): 0
		for i in range(28)
	}

	latest_sleep_hours = None
	latest_date = None

	# Add each workout's session load to its day.
	for log in logs:
		session_date = log["session_date"]

		if isinstance(session_date, str):
			session_date = date.fromisoformat(session_date)

		if session_date in daily_loads:
			session_load = int(log["duration_mins"]) * int(log["rpe"])
			daily_loads[session_date] += session_load

			if latest_date is None or session_date >= latest_date:
				latest_date = session_date
				latest_sleep_hours = log.get("sleep_hours")

	trend = []

	# Calculate metrics for each day in the 28-day window.
	for i in range(28):
		current_date = window_start + timedelta(days=i)

		# Average the available 7 calendar days.
		acute_start = max(window_start, current_date - timedelta(days=6))
		acute_days = [
			acute_start + timedelta(days=j)
			for j in range((current_date - acute_start).days + 1)
		]
		acute_load = sum(daily_loads[d] for d in acute_days) / len(acute_days)

		# Average all available days in the 28-day window up to this date.
		chronic_days = [window_start + timedelta(days=j) for j in range(i + 1)]
		chronic_load = sum(daily_loads[d] for d in chronic_days) / len(chronic_days)

		acwr = acute_load / chronic_load if chronic_load > 0 else 0

		trend.append({
			"date": current_date.isoformat(),
			"acute_load": round(acute_load, 2),
			"chronic_load": round(chronic_load, 2),
			"acwr": round(acwr, 2),
		})

	# Today's values are the final trend values.
	latest = trend[-1]

	return {
		"acute_load": latest["acute_load"],
		"chronic_load": latest["chronic_load"],
		"acwr": latest["acwr"],
		"risk_status": get_risk_status(latest["acwr"]),
		"latest_sleep_hours": latest_sleep_hours,
		"trend": trend,
	}


def get_athlete_metrics(athlete_id):
	"""Get complete ACWR metrics for one athlete."""
	athlete = get_athlete(athlete_id)

	if athlete is None:
		raise ValueError("Athlete not found")

	logs = get_logs(athlete_id, days=28)
	metrics = calculate_metrics(logs)

	return {
		"athlete_id": athlete["id"],
		"name": athlete["name"],
		"sport": athlete["sport"],
		**metrics,
	}


def list_athlete_metrics():
	"""Get ACWR metrics for every athlete."""
	athletes = list_athletes()

	return [get_athlete_metrics(athlete["id"]) for athlete in athletes]
