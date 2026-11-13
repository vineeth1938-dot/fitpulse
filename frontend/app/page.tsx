"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { Activity } from "lucide-react";
import { getAcwr, getAthletes, type AcwrDetail, type Athlete } from "@/lib/api";
import { RISK } from "@/lib/risk";
import { AthleteCard } from "@/components/AthleteCard";
import { TrendChart } from "@/components/TrendChart";
import { LogWorkoutForm } from "@/components/LogWorkoutForm";
import { RecoveryPlanPanel } from "@/components/RecoveryPlanPanel";
import { CorridorChart } from "@/components/CorridorChart";
import { SimulateButton } from "@/components/SimulateButton";
import { FoodCoach } from "@/components/FoodCoach";
import { InjuryChat } from "@/components/InjuryChat";
import { CoachCopilot } from "@/components/CoachCopilot";

const PRIORITY_DEMO = "22222222-2222-2222-2222-222222222222";
const Panel = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <h2 className="mb-3 text-base font-semibold text-slate-900">{title}</h2>{children}
  </section>
);

export default function Dashboard() {
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AcwrDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [planTrigger, setPlanTrigger] = useState(0);
  const selectedRef = useRef<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const list = await getAthletes();
      setAthletes(list);
      setSelectedId((cur) => cur ?? list.find((a) => a.id === PRIORITY_DEMO)?.id ?? list[0]?.id ?? null);
      setError(null);
    } catch (e) { setError(e instanceof Error ? e.message : "Cannot reach the API"); }
  }, []);

  useEffect(() => { selectedRef.current = selectedId; }, [selectedId]);
  useEffect(() => { refresh(); }, [refresh]);
  useEffect(() => {
    if (!selectedId) return;
    let live = true;
    getAcwr(selectedId).then((d) => { if (live) { setDetail(d); setError(null); } }).catch((e) => live && setError(e.message));
    return () => { live = false; };
  }, [selectedId]);

  const selected = athletes.find((a) => a.id === selectedId);

  return (
    <main className="mx-auto max-w-6xl space-y-6 p-4 sm:p-8">
      <header className="flex items-center gap-3">
        <Activity className="text-indigo-700" aria-hidden />
        <div>
          <h1 className="text-2xl font-bold text-slate-900">FitPulse</h1>
          <p className="text-sm text-slate-600">Training load, fatigue and injury-risk monitoring</p>
        </div>
      </header>

      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{error}. Is the API running on port 8000?</p>}

      <div className="grid gap-4 sm:grid-cols-3">
        {athletes.map((a) => <AthleteCard key={a.id} a={a} selected={a.id === selectedId} onSelect={() => { setSelectedId(a.id); setDetail(null); setPlanTrigger(0); }} />)}
      </div>

      <ul className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-slate-700" aria-label="ACWR risk bands">
        {(Object.keys(RISK) as (keyof typeof RISK)[]).map((k) => (
          <li key={k} className="flex items-center gap-1.5">
            <span className="size-2 rounded-full" style={{ background: RISK[k].color }} aria-hidden />{k} {RISK[k].hint}
          </li>
        ))}
      </ul>

      {selected && (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-2">
            <Panel title={`${selected.name}: 28-day ACWR trend`}>
              {detail ? <TrendChart data={detail.trend} /> : <p className="text-sm text-slate-600">Loading…</p>}
              {detail && detail.trend.every((t) => t.acwr === null) && (
                <p className="mt-2 text-sm text-slate-700">Not enough history yet: the trend starts after 14 days of logged training.</p>
              )}
            </Panel>
            <Panel title="Acute vs chronic load">
              {detail ? <CorridorChart data={detail.trend} /> : <p className="text-sm text-slate-600">Loading…</p>}
            </Panel>
            <Panel title="Demo">
              <SimulateButton key={selected.id} athleteId={selected.id} onChange={(r, simulated) => {
                refresh();
                if (selected.id !== selectedRef.current) return; // user switched athlete meanwhile
                setDetail(r);
                if (simulated && r.acwr > 1.5) setPlanTrigger((n) => n + 1);
              }} />
            </Panel>
            <Panel title="Log a workout">
              <LogWorkoutForm key={selected.id} athleteId={selected.id} onLogged={(r) => {
                if (selected.id === selectedRef.current) setDetail(r); // ignore if the user switched athlete meanwhile
                refresh();
              }} />
            </Panel>
          </div>
          <div className="space-y-6">
            <Panel title="48h deload plan"><RecoveryPlanPanel key={selected.id} athleteId={selected.id} trigger={planTrigger} /></Panel>
            <Panel title="Coach copilot"><CoachCopilot /></Panel>
            <Panel title="Food photo coach"><FoodCoach key={selected.id} /></Panel>
            <Panel title="Injury prevention chat"><InjuryChat key={selected.id} /></Panel>
          </div>
        </div>
      )}
    </main>
  );
}
