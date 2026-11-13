# FitPulse

AI-driven training load, fatigue and injury-risk monitoring for amateur and student athletes.

Coaches log each session (minutes and effort), and FitPulse turns it into an **Acute:Chronic Workload Ratio (ACWR)** per athlete, flags injury risk early, and uses AI to coach recovery, nutrition and injury prevention. No wearables or GPS vests are needed.

## What it does

- **Roster dashboard:** every athlete with their ACWR and a risk badge (Safe, Caution, Danger, Undertraining).
- **28-day charts:** ACWR trend, plus acute vs chronic load.
- **48h recovery plan:** an AI deload plan with mobility drills and a nutrition tip.
- **Coach copilot:** ask about your squad in plain language and get answers with names and numbers.
- **Food photo coach:** upload a meal photo, pick a goal (slim, cut, bulk or healthy), and get calories, macros and a matching workout plan.
- **Injury prevention chat:** asks up to 5 short questions about the pain, then suggests prevention exercises and technique tips. It never diagnoses.
- **One-click demo:** "Simulate brutal practice" logs a 120-minute, RPE 9 session so you can watch an athlete go from green to red. "Reset demo" undoes it.

## How ACWR is calculated

- Session load = minutes × RPE (effort, 1 to 10).
- Daily load = the sum of that day's sessions. Rest days count as 0.
- Acute load = average daily load over the last 7 days. Chronic load = average over the last 28 days.
- ACWR = acute ÷ chronic.

| ACWR | Status |
|---|---|
| below 0.80 | Undertraining |
| 0.80 to 1.30 | Safe |
| 1.31 to 1.50 | Caution |
| above 1.50 | Danger |

## Stack

- **Database:** Supabase (PostgreSQL), see `db/schema.sql`
- **Backend:** Python, FastAPI, Uvicorn (`backend/`)
- **Frontend:** Next.js, TypeScript, Tailwind, Recharts (`frontend/`)
- **AI:** Sarvam AI (`sarvam-105b`) for recovery plans, the copilot and the injury chat. Google Gemini reads meal photos.

## Run it locally

You need Python 3.12 (tested), Node 20 or newer, a Supabase project, and API keys for Sarvam AI and Google Gemini.

**1. Database.** In the Supabase SQL Editor, run `db/schema.sql`, then `db/seed.sql`. This loads 10 demo athletes. The schema drops and recreates both tables, so only run it on a fresh or demo project.

**2. Backend.**

```bash
cd backend
cp .env.example .env        # then fill in the keys (see below)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn main:app --port 8000
```

**3. Frontend.** In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

If a port is already taken, Next.js picks the next free one (for example 3001) and the API then rejects its requests. Start the backend with `CORS_ORIGINS=http://localhost:3001`, or whichever address Next.js printed. To run the API on a different port, start the frontend with `NEXT_PUBLIC_API_URL=http://localhost:8001`.

## Keys (`backend/.env`)

| Variable | What it is |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | A Supabase **secret** (service role) key. It stays on the server only. |
| `SARVAM_API_KEY` | Sarvam AI key |
| `GEMINI_API_KEY` | Google Gemini key, used for meal photos |
| `CORS_ORIGINS` | Optional. Comma-separated allowed frontend origins. Default: `http://localhost:3000` |

Never commit `.env`. It is in `.gitignore`.

## API

Interactive docs are at http://localhost:8000/docs once the backend is running.

| Endpoint | Purpose |
|---|---|
| `GET /athletes` | Every athlete with ACWR, acute and chronic load, and risk status |
| `GET /athletes/{id}/acwr` | One athlete's ACWR and 28-day trend |
| `POST /workouts` | Log a session and get the recalculated ACWR |
| `DELETE /athletes/{id}/simulated-workouts` | Remove the demo session |
| `POST /athletes/{id}/recovery-plan` | AI 48h recovery plan |
| `POST /coach-copilot` | Ask a question about the whole squad |
| `POST /food-analysis` | Meal photo (JPEG, PNG or WebP, up to 5 MB) and goal, returns calories and a workout plan |
| `POST /injury-chat` | Injury prevention chat, at most 5 questions |

## Tests

```bash
cd backend && .venv/bin/pytest
```

## Known limits

- There is no login and no rate limiting. The endpoints are open by design for the demo, so add both before any public deployment.
- Calorie figures from a photo are estimates. The injury chat and recovery plans are not medical advice.

## Team workflow

Never push to `main`. Work on your own branch and open a pull request. See `TEAM_GUIDE.md` for roles and details.
