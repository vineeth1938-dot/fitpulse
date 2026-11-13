"use client";
import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { injuryChat, type ChatTurn } from "@/lib/api";

const MAX_QUESTIONS = 5;

export function InjuryChat() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const logEnd = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const newChatRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { logEnd.current?.scrollIntoView({ block: "end" }); }, [turns, busy]);
  useEffect(() => { if (done) newChatRef.current?.focus(); }, [done]); // the input unmounts when the chat ends
  const asked = turns.filter((t) => t.role === "assistant").length;

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const text = q.trim();
    if (!text || busy || done) return;
    const next: ChatTurn[] = [...turns, { role: "user", content: text }];
    setTurns(next); setQ(""); setBusy(true); setError(null);
    try {
      const r = await injuryChat(next);
      setTurns([...next, { role: "assistant", content: r.reply }]);
      setDone(r.done);
    } catch (err) {
      setTurns(turns); setQ((cur) => cur || text); // roll back so the athlete can retry
      setError(err instanceof Error ? err.message : "Failed");
    } finally { setBusy(false); }
  }

  return (
    <div className="space-y-3 text-sm">
      <p className="text-slate-700">Describe your pain. I will ask up to {MAX_QUESTIONS} short questions, then suggest exercises and technique tips. This is not a diagnosis.</p>
      <div role="log" aria-label="Injury chat" tabIndex={0} className="max-h-72 space-y-2 overflow-y-auto">
        {turns.map((t, i) => (
          <p key={i} className={t.role === "user" ? "font-medium text-slate-900" : "whitespace-pre-wrap rounded-lg bg-slate-100 p-3 text-slate-800"}>{t.content}</p>
        ))}
        {busy && <p className="text-slate-600">Thinking…</p>}
        <div ref={logEnd} />
      </div>
      {asked > 0 && !done && <p className="text-xs text-slate-600">Question {Math.min(asked, MAX_QUESTIONS)} of {MAX_QUESTIONS}</p>}
      {error && <p role="alert" className="text-red-700">{error}</p>}
      {done ? (
        <button ref={newChatRef} onClick={() => { setTurns([]); setDone(false); requestAnimationFrame(() => inputRef.current?.focus()); }} className="rounded-lg border border-slate-300 px-3 py-2 font-medium text-slate-800 hover:bg-slate-100">Start a new chat</button>
      ) : (
        <form onSubmit={send} className="flex gap-2">
          <input ref={inputRef} disabled={busy} value={q} onChange={(e) => setQ(e.target.value)} maxLength={1000} aria-label="Describe your pain or answer the question"
            placeholder={turns.length ? "Your answer…" : "e.g. my knee hurts when I run downhill"}
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2" />
          <button disabled={busy} aria-label="Send" className="rounded-lg bg-indigo-700 px-3 text-white hover:bg-indigo-800 disabled:opacity-60"><Send size={16} aria-hidden /></button>
        </form>
      )}
    </div>
  );
}
