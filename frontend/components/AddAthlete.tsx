"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { UserPlus } from "lucide-react";
import { createAthlete, type Athlete } from "@/lib/api";

const field = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm";

export function AddAthlete({ onAdded }: { onAdded: (a: Athlete) => void }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const toggle = useRef<HTMLButtonElement>(null);
  const wasOpen = useRef(false);
  useEffect(() => { // the form unmounts when it closes, so hand focus back to the button
    if (wasOpen.current && !open) toggle.current?.focus();
    wasOpen.current = open;
  }, [open]);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const f = new FormData(form);
    const hr = String(f.get("hr") ?? "").trim();
    setBusy(true); setError(null);
    try {
      const athlete = await createAthlete({
        name: String(f.get("name")).trim(),
        sport: String(f.get("sport") ?? "").trim() || undefined,
        position: String(f.get("position") ?? "").trim() || undefined,
        resting_hr: hr ? Number(hr) : undefined,
      });
      form.reset(); setOpen(false);
      onAdded(athlete);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add the athlete");
    } finally { setBusy(false); }
  }

  if (!open) {
    return (
      <button ref={toggle} type="button" onClick={() => setOpen(true)}
        className="inline-flex items-center gap-2 rounded-lg bg-indigo-700 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-800">
        <UserPlus size={16} aria-hidden /> Add athlete
      </button>
    );
  }
  return (
    <form onSubmit={submit} className="grid w-full gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:grid-cols-4">
      <label className="text-sm font-medium text-slate-700 sm:col-span-2">Name
        <input name="name" required maxLength={60} autoFocus className={field} /></label>
      <label className="text-sm font-medium text-slate-700">Sport
        <input name="sport" maxLength={40} className={field} /></label>
      <label className="text-sm font-medium text-slate-700">Position
        <input name="position" maxLength={40} className={field} /></label>
      <label className="text-sm font-medium text-slate-700">Resting heart rate (optional)
        <input name="hr" type="number" min={25} max={120} className={field} /></label>
      <div className="flex items-end gap-2 sm:col-span-3">
        <button disabled={busy} className="rounded-lg bg-indigo-700 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-800 disabled:opacity-60">
          {busy ? "Adding…" : "Add athlete"}</button>
        <button type="button" onClick={() => { setOpen(false); setError(null); }}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-800 hover:bg-slate-100">Cancel</button>
      </div>
      {error && <p role="alert" className="text-sm text-red-700 sm:col-span-4">{error}</p>}
    </form>
  );
}
