# FitPulse: Hackathon Day Guide (plain English, step by step)

Read this top to bottom. Do only YOUR part (Member 1, 2, 3 or 4) plus Parts 1, 7, 8 and 12 (everyone).
Whenever you see a box of text like this, you copy it exactly:

```
this is a command or a prompt
```

**Commands** go in the **terminal**. **Prompts** go to Claude (or your AI tool). Never type the ``` marks.

---

## 0. Read this first

### Words you will hear
| Word | Plain meaning |
|---|---|
| **Terminal** | A black window where you type commands. In VS Code: top menu **Terminal** -> **New Terminal**. |
| **Repo** | The project folder that lives on GitHub so all 4 of us share it. |
| **Clone** | Download the repo to your laptop (once). |
| **Branch** | Your own copy of the project to work in, so you don't break the others. |
| **Commit** | Save your work with a note. |
| **Push** | Upload your saved work to GitHub. |
| **Pull Request (PR)** | Ask to add your work to the main project. |
| **Merge** | Add your work to the main project. |
| **API / endpoint** | A web address the frontend calls to get data (like `http://localhost:8000/athletes`). |
| **.env file** | A secret notes file with passwords/keys. Never share it, never upload it. |

### Who is who
| Member | Job | Branch | Your folder/file |
|---|---|---|---|
| **1** | Backend and ACWR math (team lead) | `feat/backend` | `backend/` (not `agents.py`) |
| **2** | Frontend dashboard | `feat/frontend` | `frontend/` |
| **3** | AI agents | `feat/ai-agents` | `backend/agents.py` |
| **4** | Database, testing, pitch deck | `feat/seed-data` | `db/`, deck |

### The 5 rules
1. Only touch YOUR files.
2. Never push to `main`. Push to your own branch, then open a PR.
3. Never share keys in chat or GitHub. `.env` stays on your laptop.
4. If you get an error, copy the whole red text, paste it to Claude, and say: `I got this error. Fix it and explain it simply.`
5. Small steps. Save (commit) every time something works.

### The 24-hour clock (adjust to your event start; take breaks and sleep in shifts)
| Hours | What happens |
|---|---|
| 0:00 - 0:45 | Everyone: laptop setup (Part 1) |
| 0:45 - 1:30 | Member 4 builds the database; Member 1 starts backend |
| 1:30 - 5:00 | Members 1, 2, 3 build their parts |
| 5:00 - 8:00 | Everyone sends PRs; we connect everything (Part 8) |
| 8:00 - 10:00 | The demo button (Part 9) |
| 10:00 - 16:00 | Polish, testing, better AI answers |
| 14:00 - 19:00 | Pitch deck and demo video (Member 4 + all) |
| 19:00 - 21:30 | Final testing, fix only big bugs |
| 21:30 - 22:00 | FREEZE: no new features |
| 22:00 - 24:00 | Rehearse the pitch 3 times, submit |

---

## 1. Everyone: set up your laptop (first 45 minutes)

### 1A. Member 1 only: invite the team on GitHub
1. Go to **github.com** and log in.
2. Open **github.com/vineeth1938-dot/fitpulse**.
3. Click the **Settings** tab (top row, far right).
4. Left side menu: click **Collaborators**. (GitHub may ask for your password.)
5. Click the green **Add people** button.
6. Type a teammate's GitHub username, click their name when it shows, then click **Add ... to this repository**.
7. Do this for all 3 teammates. (Need a GitHub account? Go to github.com and click **Sign up**.)

### 1B. Teammates: accept the invite
1. Open your email or the bell icon on github.com.
2. Click **Accept invitation**.

### 1C. Everyone: install 5 free things
Download and install each. Click Next/OK on everything.
1. **VS Code** (the editor): code.visualstudio.com
2. **Git**: git-scm.com/downloads
3. **Node.js** (choose the LTS button): nodejs.org
4. **Python 3.10 or newer**: python.org/downloads (on Windows, tick **Add Python to PATH**)
5. **GitHub CLI**: cli.github.com

Close and reopen VS Code. Then check everything: open **Terminal -> New Terminal** and type:
```
git --version && node -v && python3 --version && gh --version
```
You should see four version numbers. (On Windows, if `python3` fails, type `python --version` instead and use `python` wherever this guide says `python3`.)

### 1D. Everyone: log in to GitHub and download the project
Type these one at a time:
```
gh auth login
```
Choose: **GitHub.com** -> **HTTPS** -> **Yes** -> **Login with a web browser**. Copy the code it shows, press Enter, paste the code in the browser page, click **Authorize**.

Tell git who you are (use your own name and email):
```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Download the project:
```
gh repo clone vineeth1938-dot/fitpulse
cd fitpulse
```

Switch to YOUR branch (pick yours):
```
git checkout feat/backend
```
or `git checkout feat/frontend` or `git checkout feat/ai-agents` or `git checkout feat/seed-data`.

Now in VS Code: **File -> Open Folder** -> choose the `fitpulse` folder.

### 1E. Your secret keys file
1. In the terminal, type: `cp backend/.env.example backend/.env` (Windows: `copy backend\.env.example backend\.env`)
2. In VS Code's left panel open `backend` and click the file `.env`.
3. Fill in the three lines. Paste each value right after the `=` with no spaces and no quotes:
```
SUPABASE_URL=https://etnudukhgyoopupodfby.supabase.co
SUPABASE_KEY=(Member 1 sends you this privately, in a one-to-one message)
SARVAM_API_KEY=(your own key from the hackathon organizers / Sarvam dashboard)
```
4. Press **Ctrl+S** to save.
5. Only Members 1, 3 and 4 really need the Supabase key. Member 2 can leave it empty until Part 8.

### 1F. Using Claude Code in your folder
Open the terminal in the fitpulse folder and type `claude`. When it starts, type `FITPULSE` and press Enter. It shows the skills for your role. Pick your member number.

---

## 2. Member 1: Start of the day (do this first, 5 minutes)

The database files are in your own folder but not on GitHub yet. In Claude, type:
```
Push db/ to main on GitHub (docs only, no secrets), then create no other files.
```
Check it worked: open github.com/vineeth1938-dot/fitpulse and see a folder called `db`. Tell Member 4 "db is on GitHub".

---

## 3. Member 4: The database (Hour 0:45 to 1:30)

Why first: with no data, the dashboard is empty. Everyone waits for you.

1. In the terminal: `git checkout feat/seed-data` then `git pull origin main --no-edit`.
2. Go to **supabase.com** and log in. Click your project **Fitpulse**. (Member 1 invites you first: **Organization settings -> Team -> Invite**, your email, role **Developer**. Accept the email.)
3. Left menu: click **SQL Editor** (icon looks like `>_`).
4. Click **New query**.
5. In VS Code open the file `db/schema.sql`. Press **Ctrl+A** then **Ctrl+C** (select all, copy).
6. Click in the Supabase editor, press **Ctrl+V**, then click the green **Run** button.
   - It says it will delete old tables: that is fine, they only had a test row.
   - You should see "Success. No rows returned".
7. Click **New query** again. Open `db/seed.sql` in VS Code, copy all, paste, click **Run**.
8. Left menu: **Table Editor**. Click `athletes`: 3 rows (Aarav, Priya, Rohan). Click `workout_logs`: 49 rows.
9. Check the numbers. New query, paste this, click **Run**:
```
select a.name,
  round((sum(case when w.session_date > current_date - 7 then w.duration_mins * w.rpe else 0 end) / 7.0)::numeric, 1) as acute,
  round((sum(w.duration_mins * w.rpe) / 28.0)::numeric, 1) as chronic,
  round(((sum(case when w.session_date > current_date - 7 then w.duration_mins * w.rpe else 0 end) / 7.0) /
         (sum(w.duration_mins * w.rpe) / 28.0))::numeric, 2) as acwr
from athletes a join workout_logs w on w.athlete_id = a.id
where w.session_date > current_date - 28
group by a.name;
```
You must see about: **Aarav 1.68, Priya 1.06, Rohan 1.36**. If not, tell Member 1.
10. Tell the team: "data is live".
11. Then start your next jobs: Part 10 (testing plan) and Part 11 (pitch deck).

(Why Priya works for the demo: she trains 3 days a week and today is a rest day. A rest day counts as zero. So one huge session today pushes her ACWR above 1.5.)

---

## 4. Member 1: The backend (Hour 1 to 5)

### Step 1: Get set up
In the terminal (make sure you are on your branch: `git checkout feat/backend`):
```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi "uvicorn[standard]" supabase python-dotenv pydantic sarvamai pytest httpx
pip freeze > requirements.txt
```
Windows: use `.venv\Scripts\activate` instead of the `source` line. When it works, the line starts with `(.venv)`.

### Step 2: Ask Claude to build it
Type `claude` in the terminal (inside the `backend` folder) and paste this whole prompt:
```
Read ../CLAUDE.md. Build the FitPulse backend in backend/ using FastAPI and Supabase. Keep the code simple and modular.

Files:
1. backend/db.py: make the Supabase client from SUPABASE_URL and SUPABASE_KEY in backend/.env (python-dotenv). Functions: list_athletes(), get_athlete(athlete_id), get_logs(athlete_id, days=28) returning workout_logs for the last N days, get_recent_workouts(athlete_id, n=3) newest first, insert_workout(data).
2. backend/acwr.py: the math. Daily load = sum of duration_mins * rpe of all sessions on that date. Days with no session count as load 0. Acute = average daily load over the last 7 days. Chronic = average daily load over the last 28 days. ACWR = acute / chronic, rounded to 2 decimals (if chronic is 0 then ACWR is 0). risk_status: ACWR below 0.80 is "Undertrained"; up to 1.30 is "Safe"; up to 1.50 is "Caution"; above 1.50 is "Danger". Trend array: one entry per day for the last 28 days, each {date, acute_load, chronic_load, acwr}; for each date D, acute averages the days D-6..D and chronic averages the days D-27..D, but only over days inside the 28-day data window (do not count days before the data starts as zeros). For today the trend value must equal the headline numbers. Also expose these two functions that another teammate (agents.py) will import, with EXACTLY these names: get_athlete_metrics(athlete_id) returning a dict {athlete_id, name, sport, acwr, acute_load, chronic_load, risk_status, latest_sleep_hours, trend} and list_athlete_metrics() returning a list of those dicts.
3. backend/schemas.py: pydantic models for the requests/responses.
4. backend/main.py: the FastAPI app with CORS allowing http://localhost:3000 and http://127.0.0.1:3000, and these endpoints exactly as in CLAUDE.md: GET /athletes, GET /athletes/{id}/acwr, POST /workouts (insert the workout, then return the recalculated metrics). Do NOT create the recovery-plan or coach-copilot endpoints; Member 3 owns backend/agents.py.
5. backend/tests/test_acwr.py: pytest tests for the math using fake logs. Expected values: Priya about 1.06 (acute 167.1, chronic 157.5), Priya after adding one 120 min RPE 9 session today about 1.64, Aarav about 1.68, Rohan about 1.36.
Run the tests and make them pass. Do not touch any .env file.
```
Wait until Claude finishes. When it asks permission to run things, read and say yes.

### Step 3: Run it
```
uvicorn main:app --reload --port 8000
```
Leave this window open. Open a browser: **http://localhost:8000/docs**
1. Click `GET /athletes`, click **Try it out**, click **Execute**. You should see 3 athletes with `acwr` and `risk_status`.
2. Aarav should be "Danger" (~1.68), Priya "Safe" (~1.06), Rohan "Caution" (~1.36).
If something is wrong, copy the error, paste to Claude: `I got this error. Fix it and explain it simply.`

### Step 4: Send it
Open a SECOND terminal (the first is running the server):
```
cd ~/fitpulse
git add backend/db.py backend/acwr.py backend/schemas.py backend/main.py backend/tests backend/requirements.txt
git commit -m "Add backend: ACWR engine and endpoints"
git push -u origin feat/backend
```
Then do Part 7 (open the Pull Request). Tell the team: "backend is up, pull main".

### Step 5 (after Member 3's PR is merged): connect the AI routes
In Claude:
```
Read backend/agents.py. It exposes an APIRouter named router. In backend/main.py import it and include it with app.include_router(router). Do not change anything else. Then run the server and check /docs shows the two AI endpoints.
```

---

## 5. Member 3: The AI agents (Hour 1 to 6)

You use **Sarvam AI** (the model `sarvam-105b`). Rules for this model: it "thinks" first, so ALWAYS set `max_tokens` to 1500 or more, or the answer comes back empty.

### Step 1: Get set up
```
git checkout feat/ai-agents
git pull origin main --no-edit
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install sarvamai fastapi "uvicorn[standard]" supabase python-dotenv pydantic
```
(Windows: `.venv\Scripts\activate`.) Put your `SARVAM_API_KEY` in `backend/.env` (Part 1E).

### Step 2: Build and test the AI part alone (no need to wait for Member 1)
Type `claude` in the `backend` folder and paste:
```
Read ../CLAUDE.md. Create backend/agents.py (only this file) using the Sarvam AI SDK: from sarvamai import SarvamAI; client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"]); response = client.chat.completions_v2(model="sarvam-105b", messages=[...], max_tokens=2000); the answer text is response.choices[0].message.content. Load the key from backend/.env with python-dotenv. Never print the key.
Write these functions:
1. build_recovery_prompt(metrics: dict, recent_workouts: list) -> list of chat messages. System message: an elite sports physiologist. User message includes ACWR, acute load, chronic load, risk status, last sleep hours and the last 3 workouts. Ask for ONLY a JSON object with keys: risk_summary (string), deload_percentage (integer), mobility_drills (a list of exactly 3 strings), nutrition_hydration_tip (string). No markdown.
2. parse_json(text) -> dict: strip any code fences, find the first { and last }, json.loads it. If it fails, ask Sarvam one more time, then return a safe default plan.
3. generate_recovery_plan(metrics, recent_workouts) -> dict with exactly the 4 keys.
4. answer_coach_question(question: str, all_metrics: list) -> str: put every athlete's name, ACWR, acute, chronic, risk_status and latest sleep into the prompt and require the answer to name athletes and quote their numbers.
At the bottom add an if __name__ == "__main__" demo that prints a recovery plan for Priya Nair with ACWR 1.64, acute 321.4, chronic 196.1, Danger, sleep 5.5, last workouts 120 min RPE 9 today and 65 min RPE 6, and prints the coach answer to "Who is most at risk this week?" using three fake athletes (Aarav 1.68 Danger, Priya 1.64 Danger, Rohan 1.36 Caution).
```
Run it:
```
python agents.py
```
You should see a JSON recovery plan and a sentence naming athletes. If the answer is empty, raise `max_tokens` (tell Claude: `The answer is empty, raise max_tokens`).

### Step 3: Make it nicer (spend time here, judges love this)
Ask Claude: `Make the recovery plan more specific: 48-hour plan, exact mobility drills with sets/reps, a hydration target in litres. Keep the same 4 JSON keys.`

### Step 4: Send it
```
git add backend/agents.py
git commit -m "Add AI agents with Sarvam"
git push -u origin feat/ai-agents
```
Open the Pull Request (Part 7).

### Step 5: After Member 1's backend is merged, add the web endpoints
```
git checkout feat/ai-agents
git pull origin main --no-edit
```
Then in Claude:
```
Read backend/acwr.py and backend/db.py (do not edit them). In backend/agents.py add a FastAPI APIRouter named router with two endpoints exactly as in ../CLAUDE.md: POST /athletes/{athlete_id}/recovery-plan (use acwr.get_athlete_metrics and db.get_recent_workouts, return the 4-key JSON) and POST /coach-copilot with body {"question": str} (use acwr.list_athlete_metrics, return {"answer": str}). If Sarvam fails or times out, return a pre-written fallback plan or answer so the demo never shows an error. Do not edit other files.
```
Commit, push, and tell Member 1 "agents router is ready to mount".

---

## 6. Member 2: The frontend (Hour 1 to 6)

### Step 1: Create the app
```
git checkout feat/frontend
git pull origin main --no-edit
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --use-npm --no-src-dir --import-alias "@/*"
```
If it asks questions, press **Enter** to accept each default. Then:
```
cd frontend
npm install recharts lucide-react
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```
Open **http://localhost:3000**. You should see the starter page. Leave this running.

### Step 2: Build the dashboard with fake data first
Open a second terminal, `cd frontend`, type `claude`, and paste:
```
Read ../CLAUDE.md. In frontend/, build a dark-mode sports science dashboard called FitPulse with Next.js App Router, Tailwind, Lucide icons and Recharts. Use FAKE data from frontend/lib/mock.ts for now (3 athletes: Aarav ACWR 1.68 Danger, Priya ACWR 1.06 Safe, Rohan ACWR 1.36 Caution, each with a 28-day trend array of {date, acute_load, chronic_load, acwr}).
Layout:
- Top bar: FitPulse logo + name, an athlete dropdown, and a big red button "Simulate Brutal Practice".
- Four KPI cards: Acute Load (7d), Chronic Load (28d), ACWR Ratio with a colored pill (green 0.8 to 1.3 Safe, yellow 1.31 to 1.5 Caution, red above 1.5 Danger, gray-blue below 0.8 Undertrained), and Sleep & Recovery Score.
- Main chart (about 65% width): Recharts ComposedChart with acute and chronic load lines over 28 days and a green shaded ReferenceArea marking the 0.8 to 1.3 sweet spot.
- Right panel (about 35%): two tabs, "AI Recovery Plan" (shows risk summary, deload percentage, 3 mobility drills, nutrition tip) and "Coach Copilot" (a chat box to ask questions).
- A "+ Log Workout" button opening a modal with a duration slider (10 to 180 minutes), an RPE 1 to 10 selector, a sleep hours input and a Save button.
Make it look professional, big readable numbers, smooth color change when the risk changes. Put API calls in frontend/lib/api.ts later, not now.
```
Check http://localhost:3000. Click around. Ask Claude to fix anything ugly ("make the chart taller", "the pill is too small").

Prefer a visual tool? Go to **v0.dev**, paste the same prompt, then copy what it makes into `frontend/` (click **Code** and follow what it shows). Then use Claude to fix errors.

### Step 3: Save your work
```
git add frontend
git commit -m "Add dashboard UI with mock data"
git push -u origin feat/frontend
```
Open the Pull Request (Part 7).

### Step 4: Connect to the real backend (after Member 1's backend is merged)
```
git checkout feat/frontend
git pull origin main --no-edit
```
Ask Member 1 to send you the Supabase key privately if you want to run the backend yourself (copy it into `backend/.env`; run `cd backend && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --port 8000`). Or point `NEXT_PUBLIC_API_URL` at Member 1's laptop if you share Wi-Fi.
Then in Claude (in `frontend/`):
```
Replace the mock data with real calls in frontend/lib/api.ts using process.env.NEXT_PUBLIC_API_URL: GET /athletes for the dropdown; GET /athletes/{id}/acwr for KPI cards and the chart (use the trend array); POST /workouts for the Log Workout modal and for the Simulate Brutal Practice button (for the athlete selected: session_date today, duration_mins 120, rpe 9, sleep_hours 5.5, notes "Simulated brutal practice") then reload the ACWR; POST /athletes/{id}/recovery-plan for the AI Recovery Plan tab (call it automatically after the simulate button when the risk becomes Danger); POST /coach-copilot for the chat. Add loading spinners and friendly error messages. Never call Supabase or Sarvam from the browser. Keep the mock data file as a fallback if the backend is not reachable.
```

---

## 7. Everyone: Send your work (Pull Request)

1. After `git push`, open **github.com/vineeth1938-dot/fitpulse**.
2. A yellow bar says "...had recent pushes". Click **Compare & pull request**. (No bar? Click the **Pull requests** tab -> **New pull request** -> base: `main`, compare: your branch.)
3. Write one sentence of what you did. Click **Create pull request**.
4. Tell Member 1 in the group chat: "PR ready from <your name>".
5. Member 1 opens the **Pull requests** tab, clicks the PR, then **Merge pull request** -> **Confirm merge**. (If it says "conflicts", tell Member 1.)
6. After a merge, EVERYONE runs this to get the latest:
```
git checkout feat/your-branch
git pull origin main --no-edit
```

---

## 8. Putting it together (Hour 5 to 8)

Use **Member 1's laptop** as the demo laptop. Member 1:
1. Merges all PRs (backend, agents, frontend, db).
2. In a terminal:
```
cd ~/fitpulse
git checkout main
git pull origin main
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
3. In a second terminal:
```
cd ~/fitpulse/frontend
npm install
npm run dev
```
4. Open **http://localhost:3000**. Check: athletes load, the chart shows lines, the AI tabs answer.
5. If anything is broken, the owner of that part fixes it on their own branch, and sends a new PR.

---

## 9. The demo button (Hour 8 to 10)

What judges will see:
1. Open http://localhost:3000, select **Priya Nair**. The pill is **green**, ACWR about **1.06**.
2. Click **Simulate Brutal Practice**.
3. In about a second: the ACWR jumps to about **1.64**, the pill turns **red**, the chart line crosses above the green corridor, and the **AI Recovery Plan** shows a 48-hour deload with 3 mobility drills.
4. Type in Coach Copilot: `Who is at highest risk of injury right now and why?` It names Priya and Aarav with numbers.

If it doesn't work, check in order: backend running? frontend `.env.local` URL correct? Browser console (press **F12**, tab **Console**) shows an error? Copy it to Claude.

**Reset Priya before every rehearsal** (Member 4): Supabase -> SQL Editor -> New query:
```
delete from workout_logs where athlete_id = '22222222-2222-2222-2222-222222222222' and session_date = current_date;
```

---

## 10. Member 4: Testing (Hour 8 to 21)

Tick each box and report bugs in the group chat with a screenshot.

**Data**
- [ ] 3 athletes, 49 workouts, ACWR numbers match (Aarav 1.68, Priya 1.06, Rohan 1.36)

**Backend** (http://localhost:8000/docs)
- [ ] GET /athletes shows 3 athletes
- [ ] GET /athletes/{id}/acwr has `trend` with 28 entries
- [ ] POST /workouts with a bad RPE (like 15) gives an error, not a crash
- [ ] Recovery plan has all 4 keys; copilot names real athletes

**Frontend** (http://localhost:3000)
- [ ] Dropdown changes the numbers and the chart
- [ ] Pill colors: Aarav red, Priya green, Rohan yellow
- [ ] Log Workout modal saves and the chart updates
- [ ] Simulate Brutal Practice turns Priya red
- [ ] Nothing looks broken on a projector (big fonts, dark background)

**Code checks (anyone, in Claude, once at the end)**
```
/security-review
```
and
```
/code-review high
```
Fix what they find by asking Claude: `Fix the issues you found.`

---

## 11. Pitch deck and video (Member 4 leads, everyone helps)

### The 6 slides (5 minutes total, each person speaks once)
1. **Team**: 4 builders (Backend/Sports Science, Frontend, AI Agents, Data/QA)
2. **Problem**: student athletes train too hard with zero tracking, causing preventable injuries
3. **Solution**: FitPulse = live ACWR risk meter + AI recovery plans
4. **Why now**: cheap RPE data and fast AI make pro sports science affordable
5. **Product and live demo** (Part 9)
6. **Competition**: Strava and Garmin are generic; Catapult is pro-only and expensive; FitPulse is built for students

### Make it fast
Open **claude.ai** (or any AI chat) and paste:
```
Make a 6-slide pitch deck outline for a hackathon project called FitPulse: an AI platform that predicts injury risk for student athletes using the ACWR (acute:chronic workload ratio, 7-day vs 28-day average load). Slides: Team, Problem, Solution, Why Now, Product & Live Demo, Competition (vs Strava, Garmin, Catapult). For each slide give a short title, 3 short bullets (max 8 words each) and one line of speaker notes. Make it punchy and non-technical.
```
Then build the slides in **Google Slides** (slides.google.com) or **Canva** (canva.com): new presentation, paste the text, pick a dark theme, add screenshots from the real app.

### Backup demo video (do this at Hour 15)
Record the full demo in case the internet or laptop fails.
- Windows: press **Windows + G**, click the record button
- Mac: **Shift + Command + 5**
- Ubuntu: **Ctrl + Alt + Shift + R** (stop with the same keys)
Keep it under 90 seconds: Priya green -> button -> red -> AI plan -> Copilot.

### README (Member 4, 10 minutes, at Hour 18)
In Claude: `Write a README.md for this repo: what FitPulse is, the ACWR formula, how to run backend and frontend, tech stack, team, and a screenshot placeholder. Keep it short.` Save it to the repo root, commit, push, PR.

---

## 12. The final hours

- **Hour 21:30 FREEZE.** No new features. Only fix bugs that break the demo.
- Rehearse the full pitch 3 times with a timer.
- Test the demo on the REAL laptop and screen you will use. Plug in the projector and check.
- Close other apps, plug in the charger, turn off notifications.
- Have these ready: the backup video, the slides saved offline (download as PDF), and the GitHub repo link.
- Last: submit what the organizers ask for (usually the repo link, the demo video, the deck). Do it BEFORE the deadline, not at the deadline.

---

## 13. If something breaks

| Problem | Fix |
|---|---|
| `Permission denied` or 403 when you push | You didn't accept the GitHub invite, or you're on `main`. Switch: `git checkout feat/your-branch` |
| `command not found` for `git`, `node`, `python3` | Install it (Part 1C), then close and reopen the terminal |
| Browser says CORS error | Backend must allow `http://localhost:3000`. Restart `uvicorn` |
| `Address already in use` | `lsof -i :8000` then `kill <number>` (Windows: close the old terminal) |
| Supabase says 401 / invalid key | The key in `.env` has a space or a line break. Re-paste it on the SAME line as `SUPABASE_KEY=` |
| AI answer is empty / `None` | `max_tokens` too small. Use 1500 or more |
| Priya never turns red | Today must be a rest day for her, and rest days must count as 0 (reset her with the SQL in Part 9) |
| `ModuleNotFoundError` | `source .venv/bin/activate` then `pip install -r requirements.txt` |
| Git says CONFLICT | Don't panic. Tell Member 1, or ask Claude: `Help me resolve this merge conflict` |
| Totally stuck | Paste the error to Claude: `I got this error. Fix it and explain it simply.` |

---

## 14. Cheat sheet

```
git checkout feat/your-branch        # go to your branch
git pull origin main --no-edit       # get the team's latest work
git status                           # what did I change?
git add path/to/your/files           # choose what to save
git commit -m "what I did"           # save with a note
git push -u origin feat/your-branch  # upload to GitHub
```
Start the backend: `cd backend && source .venv/bin/activate && uvicorn main:app --reload --port 8000`
Start the frontend: `cd frontend && npm run dev`
API docs: http://localhost:8000/docs  |  App: http://localhost:3000
