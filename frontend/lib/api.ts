import { supabase } from "./supabase";

// Local calendar date (toISOString is UTC and is "yesterday" for early-morning users in UTC+).
export const localToday = () => new Date().toLocaleDateString("en-CA");
export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Risk = "Safe" | "Caution" | "Danger" | "Undertraining";
export interface Athlete {
  id: string; name: string; sport: string | null; position: string | null; is_demo: boolean;
  acute_load: number; chronic_load: number; acwr: number; risk_status: Risk;
}
export interface TrendPoint { date: string; acute_load: number; chronic_load: number; acwr: number | null }
export interface AcwrDetail { acute_load: number; chronic_load: number; acwr: number; risk_status: Risk; trend: TrendPoint[] }
export interface RecoveryPlan {
  risk_summary: string; deload_percentage: number; mobility_drills: string[]; nutrition_hydration_tip: string;
}
export interface WorkoutInput {
  athlete_id: string; session_date: string; duration_mins: number; rpe: number; sleep_hours: number | null; notes: string;
}

// Why the user was sent back to the sign-in screen; the screen reads it once.
let signInNotice: string | null = null;
export const takeSignInNotice = (): string | null => { const n = signInNotice; signInNotice = null; return n; };

let signingOut: Promise<unknown> | null = null;
function endSession(): Promise<unknown> {
  // local scope: do not revoke the user's other devices. One shared promise even if several requests fail together.
  signingOut ??= (supabase?.auth.signOut({ scope: "local" }) ?? Promise.resolve())
    .catch(() => undefined)
    .finally(() => { signingOut = null; });
  return signingOut;
}

async function request(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const { data } = (await supabase?.auth.getSession()) ?? { data: { session: null } }; // supabase-js refreshes expired tokens here
  if (data.session) headers.set("Authorization", `Bearer ${data.session.access_token}`);
  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (res.status === 401) {
    if (data.session) { // only a token we actually sent can have expired
      signInNotice = "Your session expired. Please sign in again.";
      await endSession();
    }
    throw new Error("Your session expired. Please sign in again.");
  }
  if (!res.ok) {
    const detail = await res.json().then((b) => b.detail).catch(() => null);
    throw new Error(typeof detail === "string" ? detail : `Request failed (${res.status})`);
  }
  return res;
}

async function call<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  return (await request(path, { ...init, headers })).json();
}

export const getAthletes = () => call<Athlete[]>("/athletes");
export const getAcwr = (id: string) => call<AcwrDetail>(`/athletes/${id}/acwr`);
export const logWorkout = (w: WorkoutInput) =>
  call<AcwrDetail>("/workouts", { method: "POST", body: JSON.stringify(w) });
export const getRecoveryPlan = (id: string) =>
  call<RecoveryPlan>(`/athletes/${id}/recovery-plan`, { method: "POST" });
export const askCopilot = (question: string) =>
  call<{ answer: string }>("/coach-copilot", { method: "POST", body: JSON.stringify({ question }) });
export const SIMULATED_NOTE = "Simulated brutal practice"; // must match backend db.SIMULATED_NOTE
export const resetDemo = (id: string) =>
  call<AcwrDetail>(`/athletes/${id}/simulated-workouts`, { method: "DELETE" });

export type Goal = "slim" | "cut" | "bulk" | "healthy";
export interface FoodAnalysis {
  foods: { name: string; grams?: number | null; calories: number }[]; total_calories: number;
  protein_g: number; carbs_g: number; fat_g: number; goal_advice: string;
  workout_plan: { activity: string; minutes: number; calories_burned: number }[]; disclaimer: string;
}
export interface ChatTurn { role: "user" | "assistant"; content: string }
export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

export async function analyzeFood(image: File, goal: Goal): Promise<FoodAnalysis> {
  const body = new FormData(); // no JSON header: the browser sets the multipart boundary
  body.append("image", image); body.append("goal", goal);
  return (await request("/food-analysis", { method: "POST", body, signal: AbortSignal.timeout(120_000) })).json();
}
export const injuryChat = (messages: ChatTurn[]) =>
  call<{ reply: string; questions_asked: number; done: boolean }>("/injury-chat", { method: "POST", body: JSON.stringify({ messages }) });
export const createDemoRoster = () => call<{ created: number }>("/demo-roster", { method: "POST" });

export interface AthleteInput { name: string; sport?: string; position?: string; resting_hr?: number }
export const createAthlete = (a: AthleteInput) => call<Athlete>("/athletes", { method: "POST", body: JSON.stringify(a) });
export const removeDemoAthletes = () => call<{ deleted: number }>("/demo-athletes", { method: "DELETE" });
