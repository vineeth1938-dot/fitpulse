"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { Activity } from "lucide-react";
import { createDemoRoster, getAcwr, getAthletes, removeDemoAthletes, type AcwrDetail, type Athlete } from "@/lib/api";
import { RISK } from "@/lib/risk";
import { supabase } from "@/lib/supabase";
import { AuthGate } from "@/components/AuthGate";
import { AddAthlete } from "@/components/AddAthlete";
import { AthleteCard } from "@/components/AthleteCard";
import { TrendChart } from "@/components/TrendChart";
import { LogWorkoutForm } from "@/components/LogWorkoutForm";
import { RecoveryPlanPanel } from "@/components/RecoveryPlanPanel";
import { CorridorChart } from "@/components/CorridorChart";
import { SimulateButton } from "@/components/SimulateButton";
import { FoodCoach } from "@/components/FoodCoach";
import { InjuryChat } from "@/components/InjuryChat";
import { CoachCopilot } from "@/components/CoachCopilot";

const DEMO_ATHLETE = "Priya Nair"; // ids differ per coach, so pick the demo athlete by name
const Panel = ({ title, children }: { title: string; children: React.ReactNode }) => (
  <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <h2 className="mb-3 text-base font-semibold text-slate-900">{title}</h2>{children}
  </section>
);

// Set when the user removes the demo squad, so it is not recreated next time the roster is empty.
async function demoRemoved(): Promise<boolean> {
  if (!supabase) return false;
  const { data, error } = await supabase.auth.getUser();
  if (error) throw error; // unknown is not "false": never re-create a squad the user removed
  return data.user?.user_metadata?.demo_removed === true;
}

export default function Page() {
  return <AuthGate>{(email) => <Dashboard email={email} />}</AuthGate>;
}

function Dashboard({ email }: { email: string }) {
  const [athletes, setAthletes] = useState<Athlete[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<AcwrDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [planTrigger, setPlanTrigger] = useState(0);
  const selectedRef = useRef<string | null>(null);
  const seedInFlight = useRef(false);
  const requestId = useRef(0); // only the newest refresh may update the screen
  const [settingUp, setSettingUp] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [removing, setRemoving] = useState(false);
  const [confirmingRemove, setConfirmingRemove] = useState(false); // in-page confirmation: browser pop-ups are blocked in some webviews
  const [notice, setNotice] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const id = ++requestId.current;
    let seeded = false; // this refresh created the squad, so its answer is the freshest even if a twin refresh started later
    try {
      let list = await getAthletes();
      if (list.length === 0) { // first sign-in: copy the demo squad into this account
        if (seedInFlight.current) return; // React StrictMode's twin refresh: the first one is creating it and will update the screen
        seedInFlight.current = true;
        try {
          if (!(await demoRemoved())) {
            seeded = true;
            setSettingUp(true);
            try { await createDemoRoster(); } catch { /* the squad may exist even if the answer was lost: check below */ }
            list = await getAthletes();
            if (list.length === 0) throw new Error("Could not set up the demo squad. Please reload the page.");
          }
        } finally {
          seedInFlight.current = false;
          setSettingUp(false);
        }
      }
      if (!seeded && id !== requestId.current) return; // a newer refresh has started; its answer wins
      setAthletes(list);
      setSelectedId((cur) => (cur && list.some((a) => a.id === cur) ? cur : list.find((a) => a.name === DEMO_ATHLETE)?.id ?? list[0]?.id ?? null));
      setError(null);
    } catch (e) {
      if (seeded || id === requestId.current) setError(e instanceof Error ? e.message : "Cannot reach the API");
    }
    if (seeded || id === requestId.current) setLoaded(true);
  }, []);

  async function removeDemo() {
    setConfirmingRemove(false);
    setRemoving(true); setNotice(null);
    try {
      if (!supabase) throw new Error("You are not signed in");
      // Remember the choice first, so an empty roster does not bring the demo squad back.
      const { error: saveError } = await supabase.auth.updateUser({ data: { demo_removed: true } });
      if (saveError) throw saveError;
      const { deleted } = await removeDemoAthletes();
      if (athletes.find((a) => a.id === selectedId)?.is_demo) setDetail(null);
      await refresh();
      setNotice(`Removed ${deleted} demo athletes.`);
    } catch (e) { setError(e instanceof Error ? e.message : "Could not remove the demo athletes"); }
    finally { setRemoving(false); }
  }

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
      <header className="flex flex-wrap items-center gap-3">
        <Activity className="text-indigo-700" aria-hidden />
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900">FitPulse</h1>
          <p className="text-sm text-slate-600">Training load, fatigue and injury-risk monitoring</p>
        </div>
        <p className="text-sm text-slate-700">{email}</p>
        <button type="button" onClick={() => void supabase?.auth.signOut().catch(() => undefined)}
          className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-800 hover:bg-slate-100">Sign out</button>
      </header>

      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-800">{error}</p>}
      {settingUp && <p role="status" className="text-sm text-slate-600">Setting up your demo squad…</p>}

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

      <div className="flex flex-wrap items-start gap-3">
        <AddAthlete onAdded={(a) => { setNotice(null); setSelectedId(a.id); setDetail(null); setPlanTrigger(0); void refresh(); }} />
        {athletes.some((a) => a.is_demo) && (confirmingRemove ? (
          <div role="group" aria-label="Confirm removing the demo athletes"
            className="flex flex-wrap items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2">
            <p className="text-sm text-red-900">Remove the demo athletes and their sessions? Athletes you added stay.</p>
            <button type="button" autoFocus onClick={() => void removeDemo()}
              className="rounded-lg bg-red-700 px-3 py-1.5 text-sm font-semibold text-white hover:bg-red-800">Yes, remove</button>
            <button type="button" onClick={() => setConfirmingRemove(false)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-800 hover:bg-slate-100">Cancel</button>
          </div>
        ) : (
          <button type="button" disabled={removing} onClick={() => setConfirmingRemove(true)}
            className="disabled:opacity-60 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100">
            {removing ? "Removing…" : "Remove demo athletes"}
          </button>
        ))}
      </div>
      {notice && <p role="status" className="text-sm text-slate-700">{notice}</p>}
      {loaded && !settingUp && athletes.length === 0 && !error && (
        <p role="status" className="text-sm text-slate-700">No athletes yet. Click Add athlete to create your first one.</p>
      )}

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
