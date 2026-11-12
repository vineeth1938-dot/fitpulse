# FitPulse

AI-driven training workload, fatigue and injury-risk monitoring for amateur and student athletes.

## Stack
- Database: Supabase PostgreSQL. Tables `athletes`, `workout_logs` (see `db/schema.sql`).
- Backend: Python FastAPI + Uvicorn, port 8000, in `backend/`. Uses `supabase-py`, `python-dotenv`, `pydantic`.
- Frontend: Next.js (App Router) + TypeScript + Tailwind + Recharts + Lucide, port 3000, in `frontend/`.
- AI: Sarvam AI (`sarvamai` SDK). Model `sarvam-105b` is a reasoning model: always pass `max_tokens >= 1500` or `content` comes back `None`. Key is `SARVAM_API_KEY`.

## ACWR rules
- Session load = `duration_mins * rpe`.
- Daily load = sum of that day's sessions. Days with no session count as 0 (rest days matter).
- Acute = average daily load over the last 7 calendar days. Chronic = average over the last 28 calendar days. ACWR = acute / chronic.
- 0.80-1.30 Safe (green); 1.31-1.50 Caution (yellow); >1.50 Danger (red); <0.80 Undertraining (blue/gray).

## API (http://localhost:8000, CORS allows http://localhost:3000)
1. `GET /athletes` -> each athlete with `acwr`, `acute_load`, `chronic_load`, `risk_status`.
2. `GET /athletes/{id}/acwr` -> acute, chronic, acwr, `risk_status` (Safe/Caution/Danger), 28-day `trend` `[{date, acute_load, chronic_load, acwr}]`.
3. `POST /workouts` `{athlete_id, session_date, duration_mins, rpe, sleep_hours, notes}` -> inserts, returns recalculated ACWR.
4. `POST /athletes/{id}/recovery-plan` -> `{risk_summary, deload_percentage, mobility_drills[3], nutrition_hydration_tip}`.
5. `POST /coach-copilot` `{question}` -> `{answer}` grounded in all athletes' ACWR data, cites names and numbers.

## Seed athletes
- Aarav Sharma `11111111-1111-1111-1111-111111111111`: ACWR ~1.68, red.
- Priya Nair `22222222-2222-2222-2222-222222222222`: ACWR ~1.06, green. Demo athlete.
- Rohan Verma `33333333-3333-3333-3333-333333333333`: ACWR ~1.36, caution.

## Team and git rules
- Never push to `main`. Work on your branch, open a Pull Request.
- Member 1 `feat/backend` -> `backend/` (except `agents.py`)
- Member 2 `feat/frontend` -> `frontend/`
- Member 3 `feat/ai-agents` -> `backend/agents.py`
- Member 4 `feat/seed-data` -> `db/`, pitch deck
- Only edit files you own. Ask the owner if you need a change elsewhere.
- Never commit `.env` files or print API keys.

## Skills roster
**Trigger:** when the user types `FITPULSE` (any case, alone in a message), reply with the table below (all members), then ask which member they are.

Skills marked (ECC) exist only for people who installed ECC (`npx ecc-universal@2.2.3 install --target claude-project --profile developer --no-hooks`). Everything else is installed per person (see the install column).

| Member | Role | Use |
|---|---|---|
| 1 Backend (lead) | FastAPI + ACWR engine | `superpowers` (test-driven-development, systematic-debugging, verification-before-completion), `ponytail`, `/security-review` before every PR, `/simplify`; (ECC) `fastapi-patterns`, `python-patterns`, `python-testing`, `api-design`, `postgres-patterns`, `contract-first`, agents `fastapi-reviewer`, `python-reviewer`, `database-reviewer`, `security-reviewer`, `tdd-guide`, command `/build-fix`; `task-observer` (installed, not activated) |
| 2 Frontend | Dashboard | `impeccable` (`/impeccable init` inside `frontend/`, then `critique`, `polish`), `hallmark` (`/hallmark <prompt>`, `audit <path>`), `ui-ux-pro-max`, `dataviz` (charts, KPI cards), `/code-review`; (ECC) `react-patterns`, `frontend-patterns`, `nextjs-turbopack`, `frontend-a11y`, `design-system`, `make-interfaces-feel-better`, `browser-qa`, agents `react-reviewer`, `typescript-reviewer`, `react-build-resolver` |
| 3 AI agents | Sarvam agents | `superpowers` (systematic-debugging, test-driven-development), `ponytail`, `/security-review` (keys, prompt injection); (ECC) `error-handling`, `eval-harness`, `ai-regression-testing`, `fastapi-patterns`, agents `silent-failure-hunter`, `python-reviewer` |
| 4 Data, QA, deck | Seed data, testing, pitch | `pptx` (pitch deck), `humanize-ppt` (deck outline + checkup; needs a renderer), `diagram-design` (architecture slide), `claude-mem:wowerpoint`, `deep-research` (competition slide), `superpowers:verification-before-completion` (QA checklist); (ECC) `frontend-slides`, `postgres-patterns`, `e2e-testing`, `browser-qa`, agent `database-reviewer` |
| Everyone | | `claude-mem:handoff` (end of day), `claude-mem:mem-search`, `find-skills` |

Notes: `/security-review`, `/code-review`, `/simplify` are built in. Skills only apply where that person uses Claude Code; Member 2 may use v0/Cursor and Member 4 may use Claude Web. The hackathon is 24 hours: keep it small.
