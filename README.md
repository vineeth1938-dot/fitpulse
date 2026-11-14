# FitPulse

AI-driven training load, fatigue and injury-risk monitoring for amateur and student athletes.

## Live demo

**https://fitpulse-sigma-eight.vercel.app**

Create an account on the sign-in page (any email, a password of 8 or more characters). You start with 10 demo athletes, so you can try everything straight away. The server sleeps when it has not been used for a while, so the first sign-in can take up to a minute.

Coaches log each session (minutes and effort), and FitPulse turns it into an **Acute:Chronic Workload Ratio (ACWR)** per athlete, flags injury risk early, and uses AI to coach recovery, nutrition and injury prevention. No wearables or GPS vests are needed.

## What it does

- **Roster dashboard:** every athlete with their ACWR and a risk badge (Safe, Caution, Danger, Undertraining).
- **28-day charts:** ACWR trend, plus acute vs chronic load.
- **48h recovery plan:** an AI deload plan with mobility drills and a nutrition tip.
- **Coach copilot:** ask about your squad in plain language and get answers with names and numbers.
- **Food photo coach:** upload a meal photo, pick a goal (slim, cut, bulk or healthy), and get calories, macros and a matching workout plan.
- **Injury prevention chat:** asks up to 5 short questions about the pain, then suggests prevention exercises and technique tips. It never diagnoses.
- **Accounts:** each coach signs in with email and password and sees only their own athletes. New accounts start with a copy of the 10 demo athletes.
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

**1. Database.** In the Supabase SQL Editor, run `db/schema.sql`, then `db/seed.sql`. This loads 10 demo athletes that act as templates. The schema drops and recreates both tables, so only run it on a fresh or demo project. If you already ran an older `schema.sql`, run `db/migrations/001_auth.sql` instead (it keeps your data).

In Supabase go to **Authentication, Sign In / Providers, Email** and turn **off** "Confirm email", so new accounts can sign in at once.

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
cp .env.example .env.local   # then fill in the Supabase URL and anon key
npm install
npm run dev
```

Open http://localhost:3000.

If a port is already taken, Next.js picks the next free one (for example 3001) and the API then rejects its requests. Start the backend with `CORS_ORIGINS=http://localhost:3001`, or whichever address Next.js printed. To run the API on a different port, start the frontend with `NEXT_PUBLIC_API_URL=http://localhost:8001`.

## Keys

**Frontend (`frontend/.env.local`)**: both are public by design.

| Variable | What it is |
|---|---|
| `NEXT_PUBLIC_API_URL` | The API address. Default `http://localhost:8000` |
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase **anon / publishable** key (Project Settings, API) |

**Backend (`backend/.env`)**

| Variable | What it is |
|---|---|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | A Supabase **secret** (service role) key. It stays on the server only. |
| `SARVAM_API_KEY` | Sarvam AI key |
| `GEMINI_API_KEY` | Google Gemini key, used for meal photos |
| `CORS_ORIGINS` | Optional. Comma-separated allowed frontend origins. Default: `http://localhost:3000` |

Never commit `.env`. It is in `.gitignore`.

## Deploy (free tiers)

**API on Render**
1. Create an account at https://render.com, then **New, Blueprint**, and pick this GitHub repo. Render reads `render.yaml`.
2. Fill in the variables it asks for: `SUPABASE_URL`, `SUPABASE_KEY`, `SARVAM_API_KEY`, `GEMINI_API_KEY`. Leave `CORS_ORIGINS` empty for now.
3. When it is live, note its URL (for example `https://fitpulse-api.onrender.com`) and check `/health`.

**Frontend on Vercel**
1. Create an account at https://vercel.com, **Add New, Project**, import this repo, and set **Root Directory** to `frontend`.
2. Add the three `NEXT_PUBLIC_` variables above. Set `NEXT_PUBLIC_API_URL` to the Render URL.
3. Deploy, and note the Vercel URL.

**Finish**
1. In Render, set `CORS_ORIGINS` to the Vercel URL (no trailing slash) and let it redeploy.
2. In Supabase, **Authentication, URL Configuration**, set **Site URL** to the Vercel URL.
3. Open the Vercel URL, create an account, and the demo squad appears.

The Render free tier sleeps after 15 minutes without traffic, and the first request then takes about a minute. Open `/health` on the API a few minutes before a demo.

## API

Interactive docs are at http://localhost:8000/docs once the backend is running.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Public health check |
| `POST /demo-roster` | Copy the demo squad into the signed-in coach's account (once) |
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

## Security notes

- Every endpoint except `/health` needs a signed-in user. A coach only ever reaches their own athletes; another coach's athlete returns 404.
- Requests are rate limited per user: 10 per minute on the AI endpoints and 60 per minute on the rest. The counters live in memory, so they reset when the server restarts and are not shared across several servers.

## Known limits

- There is no Add athlete form yet: new accounts get the demo squad.
- Calorie figures from a photo are estimates. The injury chat and recovery plans are not medical advice.

## Team workflow

Never push to `main`. Work on your own branch and open a pull request. See `TEAM_GUIDE.md` for roles and details.
