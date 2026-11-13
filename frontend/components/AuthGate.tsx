"use client";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import type { Session } from "@supabase/supabase-js";
import { Activity } from "lucide-react";
import { takeSignInNotice } from "@/lib/api";
import { supabase } from "@/lib/supabase";

const input = "mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm";

function SignIn() {
  const [mode, setMode] = useState<"in" | "up">("in");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [sessionNote] = useState(takeSignInNotice); // why we landed here, e.g. an expired session

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!supabase) return;
    const f = new FormData(e.currentTarget);
    const email = String(f.get("email")).trim();
    const password = String(f.get("password"));
    setBusy(true); setError(null); setNotice(null);
    try {
      if (mode === "in") {
        const { error: err } = await supabase.auth.signInWithPassword({ email, password });
        if (err) throw err;
      } else {
        const { data, error: err } = await supabase.auth.signUp({ email, password });
        if (err) throw err;
        if (!data.session) setNotice("If this address can be used, check your email to confirm the account, then sign in.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally { setBusy(false); }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-sm flex-col justify-center gap-6 p-6">
      <header className="flex items-center gap-3">
        <Activity className="text-indigo-700" aria-hidden />
        <div>
          <h1 className="text-2xl font-bold text-slate-900">FitPulse</h1>
          <p className="text-sm text-slate-600">Training load and injury-risk monitoring</p>
        </div>
      </header>
      <form onSubmit={submit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="text-base font-semibold text-slate-900">{mode === "in" ? "Sign in" : "Create your coach account"}</h2>
        <label className="block text-sm font-medium text-slate-700">Email
          <input name="email" type="email" required autoComplete="email" className={input} /></label>
        <label className="block text-sm font-medium text-slate-700">Password
          <input name="password" type="password" required minLength={mode === "up" ? 8 : undefined} aria-describedby={mode === "up" ? "pw-hint" : undefined}
            autoComplete={mode === "in" ? "current-password" : "new-password"} className={input} />
        </label>
        {mode === "up" && <p id="pw-hint" className="-mt-2 text-xs text-slate-600">At least 8 characters.</p>}
        <button disabled={busy} className="w-full rounded-lg bg-indigo-700 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-800 disabled:opacity-60">
          {busy ? "Please wait…" : mode === "in" ? "Sign in" : "Create account"}
        </button>
        {sessionNote && !error && <p role="status" className="text-sm text-slate-700">{sessionNote}</p>}
        {error && <p role="alert" className="text-sm text-red-700">{error}</p>}
        {notice && <p role="status" className="text-sm text-green-800">{notice}</p>}
        <button type="button" onClick={() => { setMode(mode === "in" ? "up" : "in"); setError(null); setNotice(null); }}
          className="text-sm font-medium text-indigo-800 underline">
          {mode === "in" ? "New here? Create an account" : "Have an account? Sign in"}
        </button>
      </form>
      <p className="text-xs text-slate-600">New accounts start with 10 demo athletes so you can try everything straight away.</p>
    </main>
  );
}

/** Renders the sign-in screen until there is a session, then calls children with the user's email. */
export function AuthGate({ children }: { children: (email: string) => ReactNode }) {
  const [session, setSession] = useState<Session | null | undefined>(undefined); // undefined = still checking

  useEffect(() => {
    if (!supabase) { setSession(null); return; }
    // The first event is INITIAL_SESSION, so no separate getSession() call that could land late and overwrite newer state.
    const { data } = supabase.auth.onAuthStateChange((_event, s) => setSession(s));
    return () => data.subscription.unsubscribe();
  }, []);

  if (!supabase) {
    return <main className="m-6"><p role="alert" className="rounded-lg bg-red-50 p-4 text-sm text-red-800">
      Sign-in is not configured. Set NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_ANON_KEY in frontend/.env.local.</p></main>;
  }
  if (session === undefined) return <main className="m-6"><p role="status" className="text-sm text-slate-600">Loading…</p></main>;
  if (!session) return <SignIn />;
  return <>{children(session.user.email ?? "your account")}</>;
}
