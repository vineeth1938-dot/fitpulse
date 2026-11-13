"use client";
import { useState } from "react";
import { localToday, logWorkout, type AcwrDetail } from "@/lib/api";

const today = localToday;
const field = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-600";

export function LogWorkoutForm({ athleteId, onLogged }: { athleteId: string; onLogged: (r: AcwrDetail) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    setBusy(true); setError(null); setSaved(false);
    try {
      const sleep = String(f.get("sleep") ?? "");
      onLogged(await logWorkout({
        athlete_id: athleteId, session_date: String(f.get("date")),
        duration_mins: Number(f.get("duration")), rpe: Number(f.get("rpe")),
        sleep_hours: sleep ? Number(sleep) : null, notes: String(f.get("notes") ?? ""),
      }));
      form.reset(); setSaved(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save workout");
    } finally { setBusy(false); }
  }

  return (
    <form onSubmit={submit} className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <label className="text-sm font-medium text-slate-700">Date
        <input name="date" type="date" defaultValue={today()} max={today()} required className={field} /></label>
      <label className="text-sm font-medium text-slate-700">Minutes
        <input name="duration" type="number" min={1} max={600} defaultValue={60} required className={field} /></label>
      <label className="text-sm font-medium text-slate-700">RPE (1–10)
        <input name="rpe" type="number" min={1} max={10} defaultValue={6} required className={field} /></label>
      <label className="text-sm font-medium text-slate-700">Sleep (h)
        <input name="sleep" type="number" step="0.5" min={0} max={24} placeholder="optional" className={field} /></label>
      <label className="col-span-2 text-sm font-medium text-slate-700 sm:col-span-3">Notes
        <input name="notes" maxLength={500} className={field} /></label>
      <button disabled={busy} className="self-end rounded-lg bg-indigo-700 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-800 disabled:opacity-60">
        {busy ? "Saving…" : "Log workout"}
      </button>
      {saved && <p role="status" className="col-span-full text-sm text-green-800">Workout saved. ACWR updated.</p>}
      {error && <p role="alert" className="col-span-full text-sm text-red-700">{error}</p>}
    </form>
  );
}
