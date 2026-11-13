"use client";
import { useState } from "react";
import { Send } from "lucide-react";
import { askCopilot } from "@/lib/api";

const SUGGESTIONS = ["Who should rest today?", "Who is undertrained?", "Compare Aarav and Rohan."];

export function CoachCopilot() {
  const [q, setQ] = useState("");
  const [turns, setTurns] = useState<{ q: string; a: string }[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask(question: string) {
    if (!question.trim() || busy) return;
    setBusy(true); setError(null);
    try {
      const { answer } = await askCopilot(question.trim());
      setTurns((t) => [...t, { q: question.trim(), a: answer }]); setQ("");
    } catch (e) { setError(e instanceof Error ? e.message : "Failed"); }
    finally { setBusy(false); }
  }

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button key={s} onClick={() => ask(s)} className="rounded-full border border-slate-300 px-3 py-1 text-xs text-slate-700 hover:bg-slate-100">{s}</button>
        ))}
      </div>
      <div className="max-h-72 space-y-3 overflow-y-auto" aria-live="polite">
        {turns.map((t, i) => (
          <div key={i} className="text-sm">
            <p className="font-medium text-slate-900">{t.q}</p>
            <p className="mt-1 rounded-lg bg-slate-100 p-3 text-slate-800">{t.a}</p>
          </div>
        ))}
        {busy && <p className="text-sm text-slate-600">Thinking…</p>}
      </div>
      {error && <p role="alert" className="mt-2 text-sm text-red-700">{error}</p>}
      <form onSubmit={(e) => { e.preventDefault(); ask(q); }} className="mt-3 flex gap-2">
        <input value={q} onChange={(e) => setQ(e.target.value)} maxLength={500} aria-label="Ask the coach copilot"
          placeholder="Ask about your squad…" className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-600" />
        <button disabled={busy} aria-label="Send" className="rounded-lg bg-indigo-700 px-3 text-white hover:bg-indigo-800 disabled:opacity-60"><Send size={16} /></button>
      </form>
    </div>
  );
}
