"use client";
import { useState } from "react";
import { Flame, RotateCcw } from "lucide-react";
import { localToday, logWorkout, resetDemo, SIMULATED_NOTE, type AcwrDetail } from "@/lib/api";

const btn = "inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-60";

export function SimulateButton({ athleteId, onChange }: { athleteId: string; onChange: (r: AcwrDetail, simulated: boolean) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run(simulate: boolean) {
    setBusy(true); setError(null);
    try {
      const r = simulate
        ? await logWorkout({ athlete_id: athleteId, session_date: localToday(),
            duration_mins: 120, rpe: 9, sleep_hours: null, notes: SIMULATED_NOTE })
        : await resetDemo(athleteId);
      onChange(r, simulate);
    } catch (e) { setError(e instanceof Error ? e.message : "Failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <button onClick={() => run(true)} disabled={busy} className={`${btn} bg-red-700 text-white hover:bg-red-800`}>
        <Flame size={16} aria-hidden /> Simulate brutal practice
      </button>
      <button onClick={() => run(false)} disabled={busy} className={`${btn} border border-slate-300 bg-white text-slate-800 hover:bg-slate-100`}>
        <RotateCcw size={16} aria-hidden /> Reset demo
      </button>
      <span className="text-xs text-slate-600">Logs a 120-minute, RPE 9 session today.</span>
      {error && <p role="alert" className="w-full text-sm text-red-700">{error}</p>}
    </div>
  );
}
