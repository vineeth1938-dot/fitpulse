// Local calendar date (toISOString is UTC and is "yesterday" for early-morning users in UTC+).
export const localToday = () => new Date().toLocaleDateString("en-CA");
export const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Risk = "Safe" | "Caution" | "Danger" | "Undertraining";
export interface Athlete {
  id: string; name: string; sport: string | null; position: string | null;
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

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const detail = await res.json().then((b) => b.detail).catch(() => null);
    throw new Error(typeof detail === "string" ? detail : `Request failed (${res.status})`);
  }
  return res.json();
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
