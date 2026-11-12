# FitPulse Team Guide (start to finish)

Four people, one GitHub repo, no stepping on each other. Follow the parts in order.

| Member | Role | Branch | Owns |
|---|---|---|---|
| 1 | Backend and ACWR engine (team lead, repo owner) | `feat/backend` | `backend/` except `agents.py` |
| 2 | Frontend and dashboard | `feat/frontend` | `frontend/` |
| 3 | AI agents (Sarvam) | `feat/ai-agents` | `backend/agents.py` |
| 4 | Database, QA, pitch deck | `feat/seed-data` | `db/`, deck |

Golden rules: never push to `main`; only edit files you own; never commit a `.env` file; never paste API keys into chat, GitHub or screenshots.

> Check the hackathon rules first. If code must be written only during the event, do Parts A and B beforehand (accounts, tools, empty repo) and leave Parts D onward for hackathon day.

---

## Part A. Member 1 sets up the project (once)

### A1. Make the first commit on `main`
The repo `vineeth1938-dot/fitpulse` already exists. Do not run `git init` or `gh repo create` again.
```bash
cd ~/fitpulse
git checkout -b main 2>/dev/null || git checkout main
git add .gitignore CLAUDE.md TEAM_GUIDE.md db backend/.env.example
git status        # confirm .env and .venv are NOT listed
git commit -m "Initial skeleton: guide, CLAUDE.md, db scripts"
git push -u origin main
```

### A2. Add your teammates on GitHub
1. Open github.com/vineeth1938-dot/fitpulse in your browser.
2. Click the **Settings** tab (far right of the tab row).
3. Left sidebar: **Collaborators**. GitHub may ask for your password or a code.
4. Click the green **Add people** button.
5. Type the teammate's GitHub username or email, click their name in the list, then click **Add <name> to this repository**.
6. Repeat for all 3 teammates.
7. Each teammate gets an email and a bell notification. They must click **Accept invitation**. Until they do, they cannot push.

### A3. Protect `main` (do this after A1)
1. Repo **Settings** -> left sidebar **Rules** -> **Rulesets**.
2. Click **New ruleset** -> **New branch ruleset**.
3. Name: `protect-main`. Enforcement status: **Active**.
4. Under **Bypass list** click **Add bypass** and choose **Repository admin** (so you can still fix emergencies).
5. Under **Target branches** click **Add target** -> **Include default branch**.
6. Tick **Require a pull request before merging**. Leave required approvals at 0 for speed, or set 1 for safety.
7. Tick **Block force pushes**.
8. Click **Create** at the bottom.

### A4. Create everyone's branches
```bash
for b in feat/backend feat/frontend feat/ai-agents feat/seed-data; do git push origin main:refs/heads/$b; done
```

### A5. Share secrets safely
- The Supabase project URL (`https://etnudukhgyoopupodfby.supabase.co`) is not secret; send it to the team in chat.
- Send the Supabase **secret key** to Members 3 and 4 in a private message (not a group chat, not GitHub). Each person puts it in their own `backend/.env`.
- Each member uses their **own** Sarvam API key from their hackathon credits.
- After the hackathon, rotate the Supabase secret key (Supabase -> Project Settings -> API Keys).

### A6. Let teammates into Supabase (Member 4 needs the SQL Editor)
1. supabase.com -> your organization -> **Organization settings** -> **Team**.
2. Click **Invite**, enter Member 4's email, role **Developer**, send.
3. Member 4 accepts the email invite and opens the `Fitpulse` project.

---

## Part B. Every teammate: one-time laptop setup

1. Install: git, Node 20+, Python 3.10+, `gh` (GitHub CLI). Check with:
   ```bash
   git --version && node -v && python3 --version && gh --version
   ```
2. Tell git who you are:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```
3. Log in to GitHub: `gh auth login` -> GitHub.com -> HTTPS -> Yes (authenticate git) -> Login with a web browser. Copy the one-time code, paste it in the browser, click **Authorize**.
4. Accept the repo invite (email or github.com notification bell -> **Accept invitation**).
5. Clone and enter the branch for your role:
   ```bash
   gh repo clone vineeth1938-dot/fitpulse ~/fitpulse
   cd ~/fitpulse
   git checkout feat/<your-branch>
   ```
6. Create your private env file (it is git-ignored):
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env     # paste values after each =, no spaces or quotes
   ```
   Save: `Ctrl+O`, `Enter`, `Ctrl+X`. Check without showing secrets: `sed 's/=.*/=<hidden>/' backend/.env`.

---

## Part C. Daily Git routine (everyone, every time)

```bash
cd ~/fitpulse
git checkout feat/<your-branch>
git pull origin main --no-edit        # get teammates' latest merged work
# ...do your work...
git status                            # see what changed
git add <only your files>             # e.g. git add backend/main.py
git commit -m "Short message: what you did"
git push -u origin feat/<your-branch>
```

### Open a Pull Request (PR) in the browser
1. After pushing, open the repo on github.com. A yellow banner says **feat/... had recent pushes** -> click **Compare & pull request**. (If no banner: **Pull requests** tab -> **New pull request** -> base `main`, compare your branch.)
2. Title: one line of what changed. Click **Create pull request**.
3. Ask a teammate to review, or click **Merge pull request** -> **Confirm merge** yourself when it says "No conflicts".
4. Everyone then runs `git pull origin main --no-edit` on their branch.

### Keep conflicts rare
- Merge small PRs at least every 1-2 hours.
- Only edit files you own (see table above). The `main` branch is the shared truth.
- If git says **CONFLICT**: open the listed file, find `<<<<<<<`, `=======`, `>>>>>>>`, keep the right lines, delete the markers, then `git add <file>` and `git commit`. Ask Member 1 for help.

---

## Part D. Member 4 first: database and seed data (hour 0 to 1)

Everything else looks dead without data, so this goes first.

1. Open supabase.com -> **Fitpulse** project.
2. Left sidebar: **SQL Editor** (the `>_` icon) -> **New query**.
3. Open `db/schema.sql` from the repo, copy everything, paste into the editor, click **Run** (or `Ctrl+Enter`). Expect "Success. No rows returned".
4. Click **New query** again. Paste all of `db/seed.sql`. Click **Run**.
5. Left sidebar: **Table Editor** -> click `athletes` (expect 3 rows) and `workout_logs` (expect 49 rows).
6. Run this check query. Expected: Aarav ~1.68, Priya ~1.06, Rohan ~1.36.
   ```sql
   select a.name,
     round((sum(case when w.session_date > current_date - 7 then w.duration_mins * w.rpe else 0 end) / 7.0)::numeric, 1) as acute,
     round((sum(w.duration_mins * w.rpe) / 28.0)::numeric, 1) as chronic,
     round(((sum(case when w.session_date > current_date - 7 then w.duration_mins * w.rpe else 0 end) / 7.0) /
            (sum(w.duration_mins * w.rpe) / 28.0))::numeric, 2) as acwr
   from athletes a join workout_logs w on w.athlete_id = a.id
   where w.session_date > current_date - 28
   group by a.name;
   ```
7. Commit on `feat/seed-data` and open a PR. Tell the team "data is live".

Why Priya's demo works: she trains 3 days a week and today is a rest day. Rest days count as 0, so adding one 120 min x RPE 9 session today moves her ACWR from about 1.06 to about 1.64. If everyone trained daily, one session would only reach about 1.2.

Member 4 then starts the pitch deck (Part H).

---

## Part E. Member 1: backend and ACWR engine (hours 1 to 4)

### Setup
```bash
cd ~/fitpulse/backend
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" supabase python-dotenv pydantic sarvamai
pip freeze > requirements.txt
```
Teammates later run `pip install -r requirements.txt` after activating their own venv.

### Build it with Claude Code
1. In a terminal: `cd ~/fitpulse/backend && claude`.
2. Paste this prompt:
   > Read ../CLAUDE.md. Build a modular FastAPI backend in backend/ (main.py, acwr.py, db.py, schemas.py) connected to Supabase using SUPABASE_URL and SUPABASE_KEY from backend/.env via python-dotenv. Implement GET /athletes, GET /athletes/{id}/acwr and POST /workouts exactly as the API section of CLAUDE.md. Days with no sessions count as 0 load. Enable CORS for http://localhost:3000. Do not create agents.py or touch the recovery-plan and coach-copilot routes; Member 3 owns them. Add a pytest for the ACWR math using the three seed athletes' expected values.
3. Run the server (keep this terminal open):
   ```bash
   source .venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```
4. Test in the browser: `http://localhost:8000/docs` -> click `GET /athletes` -> **Try it out** -> **Execute**. Expect 3 athletes with `risk_status`.
5. Commit and open a PR by end of hour 4. Tell teammates the API is live.

Mount Member 3's routes by adding two lines to `main.py` once their PR is merged: `from agents import router as agents_router` and `app.include_router(agents_router)`.

---

## Part F. Member 2: frontend dashboard (hours 1 to 6)

### Setup
```bash
cd ~/fitpulse
git checkout feat/frontend
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --use-npm --no-src-dir --import-alias "@/*"
cd frontend
npm install recharts lucide-react
echo 'NEXT_PUBLIC_API_URL=http://localhost:8000' > .env.local
npm run dev        # opens at http://localhost:3000
```
(`.env.local` is git-ignored by Next.js.)

### Generate the UI
1. Go to v0.dev and sign in. In the chat box paste:
   > Build a sleek dark-mode Sports Science Telemetry Dashboard called "FitPulse" for student athletes using Next.js App Router, Tailwind CSS, Lucide icons and Recharts. Top bar: logo, athlete dropdown, a prominent red "Simulate Brutal Practice" button. Four KPI cards: Acute Load (7d), Chronic Load (28d), ACWR Ratio with a color pill (green 0.8-1.3, yellow 1.3-1.5, red above 1.5), Sleep and Recovery Score. Main chart (65% width): Recharts ComposedChart comparing acute vs chronic load over 28 days with a shaded green ReferenceArea for the sweet spot. Right panel (35%): two tabs, "AI Recovery Plan" and "Coach Copilot" chat. A "+ Log Workout" modal with a duration slider and RPE 1-10 selector. Use mock data for now.
2. When the preview looks good, click **Code** (or **Add to codebase**). v0 shows a command; run it inside `frontend/`. Otherwise copy the files into `frontend/app` and `frontend/components`.
3. Replace mock data with real calls to `process.env.NEXT_PUBLIC_API_URL`:
   - Athlete dropdown -> `GET /athletes`
   - KPI cards and chart -> `GET /athletes/{id}/acwr` (the `trend` array feeds the chart)
   - Log Workout and the red button -> `POST /workouts`, then refetch ACWR
   - Recovery tab -> `POST /athletes/{id}/recovery-plan`; Copilot tab -> `POST /coach-copilot`
4. Never call Supabase or Sarvam from the browser. Only call the backend.
5. Commit and PR often. Use the mock data until Member 1's API is merged; then switch.

---

## Part G. Member 3: AI agents with Sarvam (hours 1 to 6)

1. `cd ~/fitpulse/backend && source .venv/bin/activate && pip install -r requirements.txt` (after Member 1's first merge), and set `SARVAM_API_KEY` in your `.env`.
2. Test the key: `set -a; . ./.env; set +a; python sarvam_test.py` -> prints "Hello there!".
3. In Claude Code (`cd backend && claude`) paste:
   > Read ../CLAUDE.md. Create backend/agents.py with a FastAPI APIRouter. Implement POST /athletes/{id}/recovery-plan and POST /coach-copilot as in CLAUDE.md, using the sarvamai SDK: client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"]); client.chat.completions_v2(model="sarvam-105b", messages=[...], max_tokens=2000). Read the answer from response.choices[0].message.content. Get athlete data by importing helper functions from acwr.py and db.py (do not edit them). For the recovery plan, instruct the model to return ONLY a JSON object with keys risk_summary, deload_percentage, mobility_drills (exactly 3 strings), nutrition_hydration_tip; strip markdown code fences and parse with json.loads, retrying once on failure. For the copilot, put all athletes' name, ACWR, acute, chronic, risk_status and latest sleep into the system prompt and require the answer to cite names and numbers.
4. Test at `http://localhost:8000/docs` once Member 1's `main.py` includes your router.
5. Gotchas:
   - `sarvam-105b` is a reasoning model. A small `max_tokens` leaves `content` empty (`None`). Use 1500 or more.
   - AI calls take a few seconds. Tell Member 2 to show a loading spinner.
   - Add a cached fallback plan so the live demo never shows an error.

---

## Part H. Pitch deck (Member 4, in parallel)

Slides, in order: 1 Team, 2 Problem (overtraining and preventable soft-tissue injuries, no workload tracking), 3 Solution (real-time ACWR plus autonomous AI recovery), 4 Why Now (cheap wearable and RPE data plus fast LLMs), 5 Product and Live Demo, 6 Competition (Strava/Garmin are generic; Catapult is pro-only and expensive).
Record a 60-second backup demo video as soon as the demo works.

---

## Part I. Integration and demo (hours 6 to 12)

Checkpoints:
| Time | Goal |
|---|---|
| Hour 1 | Data live in Supabase, repo set up, everyone cloned |
| Hour 4 | Backend ACWR endpoints merged |
| Hour 6 | Frontend on real data, agents merged |
| Hour 8 | "Simulate Brutal Practice" works end to end |
| Hour 10 | Polish, bug fixes, deck done, video recorded |
| Hour 11 | Full dry run twice |

Live demo script:
1. Open `http://localhost:3000`, select **Priya Nair** (green, ACWR about 1.06).
2. Click **Simulate Brutal Practice** (sends `POST /workouts`: today, 120 min, RPE 9, sleep 5.5).
3. KPI badge turns red (about 1.64), the chart line crosses above the green corridor, and the recovery plan panel shows the 48-hour deload and mobility drills.
4. Ask the Copilot: "Who is at highest injury risk right now and why?" It should name Priya, then Aarav, with numbers.
Reset between runs: in Supabase SQL Editor run `delete from workout_logs where athlete_id = '22222222-2222-2222-2222-222222222222' and session_date = current_date;`

---

## Troubleshooting
| Problem | Fix |
|---|---|
| `Permission denied` or 403 on push | You have not accepted the repo invite, or you are pushing to `main`. Push your branch. |
| Browser shows CORS error | Backend CORS must allow `http://localhost:3000`; restart uvicorn. |
| `Address already in use` | `lsof -i :8000` then `kill <PID>`. |
| Supabase HTTP 401 | Key has a space or newline in `.env`, or the wrong key was pasted. |
| Sarvam `content` is `None` | Raise `max_tokens` to 1500 or more. |
| Priya never turns red | Today must be a rest day and rest days must count as 0 in `acwr.py`. |
| `ModuleNotFoundError` | `source .venv/bin/activate` then `pip install -r requirements.txt`. |
| Merge conflict | See Part C; ask Member 1. |
