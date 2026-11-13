"use client";
import { useEffect, useState } from "react";
import { Droplets, HeartPulse, Loader2 } from "lucide-react";
import { getRecoveryPlan, type RecoveryPlan } from "@/lib/api";

export function RecoveryPlanPanel({ athleteId, trigger = 0 }: { athleteId: string; trigger?: number }) {
  const [plan, setPlan] = useState<RecoveryPlan | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generate() {
    setBusy(true); setError(null);
    try { setPlan(await getRecoveryPlan(athleteId)); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed"); }
    finally { setBusy(false); }
  }

  // trigger bumps when a simulated spike should open the plan automatically
  useEffect(() => { if (trigger > 0) void generate(); }, [trigger]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div>
      <button onClick={generate} disabled={busy}
        className="inline-flex items-center gap-2 rounded-lg bg-indigo-700 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-800 disabled:opacity-60">
        {busy ? <Loader2 size={16} className="animate-spin" aria-hidden /> : <HeartPulse size={16} aria-hidden />}
        {busy ? "Generating…" : "Generate recovery plan"}
      </button>
      {error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}
      {plan && (
        <div className="mt-4 space-y-3 text-sm text-slate-800" aria-live="polite">
          <p>{plan.risk_summary}</p>
          <p className="font-semibold">Reduce training load by {plan.deload_percentage}%</p>
          <ul className="list-disc space-y-1 pl-5">{plan.mobility_drills.map((d) => <li key={d}>{d}</li>)}</ul>
          <p className="flex gap-2"><Droplets size={16} className="mt-0.5 shrink-0 text-sky-600" aria-hidden />{plan.nutrition_hydration_tip}</p>
        </div>
      )}
    </div>
  );
}
