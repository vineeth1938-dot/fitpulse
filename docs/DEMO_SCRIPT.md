# FitPulse: 3-minute demo script

## Before you start (5 minutes before)
1. Run `db/reset_demo.sql` in the Supabase SQL Editor, then reload the app.
2. Start the API and the frontend (see the README), open the app, and sign in with the demo account.
3. Run one AI action (for example **Generate recovery plan**) so the AI services are warm, then click **Reset demo**.
4. Have a meal photo on the desktop, and the backup video ready in another window.
5. Close other apps and turn off notifications.

## The demo
| Time | Click | Say |
|---|---|---|
| 0:00 | Show the roster | "This is a coach's squad. Every athlete has a load score, and red means injury risk. Aarav and Sneha are in the danger zone." |
| 0:20 | Click **Priya Nair** | "Priya is green at 1.06. Her training load is steady." |
| 0:35 | Click **Simulate brutal practice** | "Now she logs one brutal 120-minute session at effort 9 out of 10." |
| 0:45 | She turns red (about 1.64) | "Her risk jumps instantly. This is the spike that causes non-contact injuries." |
| 0:55 | The 48h plan loads (about 30 s) | "While the AI coach writes a 48-hour recovery plan, note that this needs no wearable and no GPS vest, only minutes and effort." Read out the deload percentage and one drill. |
| 1:35 | Click **Reset demo** | "Back to normal." |
| 1:40 | **Food photo coach**: choose the photo, goal **cut**, **Analyse meal** | "An athlete snaps a meal and picks a goal." Read the calories and the first workout line. |
| 2:10 | **Injury prevention chat**: type "my knee hurts when I run downhill", answer 2 to 3 questions | "The coach asks at most five short questions, then gives prevention exercises. It never diagnoses." |
| 2:50 | Show the header | "Every coach signs in and sees only their own team." |
| 3:00 | Stop | "FitPulse: stop guessing fatigue, start predicting recovery." |

## If something goes wrong
- **AI says "AI service unavailable":** wait a few seconds and click again. Gemini is sometimes busy; the app already tries four models.
- **Page shows a sign-in screen:** sign in again. The session expired.
- **Page looks empty:** reload. The demo squad is created on the first load.
- **Nothing works:** play the backup video, and say "this is the recording of the live app".

## Numbers you can quote (all measured)
- ACWR calculation: about 0.35 ms. A full request takes about 300 ms because it includes the database.
- 72 automated backend tests pass.
- 10 demo athletes across all four risk bands.
