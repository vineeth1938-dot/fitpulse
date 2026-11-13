"use client";
import { useEffect, useState } from "react";
import { Camera, Dumbbell, Loader2 } from "lucide-react";
import { analyzeFood, MAX_IMAGE_BYTES, type FoodAnalysis, type Goal } from "@/lib/api";

const GOALS: Goal[] = ["slim", "cut", "bulk", "healthy"];

export function FoodCoach() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [goal, setGoal] = useState<Goal>("healthy");
  const [result, setResult] = useState<FoodAnalysis | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!file) { setPreview(null); return; }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  function pick(f: File | undefined) {
    setResult(null); setError(null);
    if (f && f.size > MAX_IMAGE_BYTES) { setError("Image must be under 5 MB"); setFile(null); return; }
    setFile(f ?? null);
  }

  async function analyze() {
    if (!file) return;
    setBusy(true); setError(null);
    try { setResult(await analyzeFood(file, goal)); }
    catch (e) { setError(e instanceof Error ? e.message : "Failed"); }
    finally { setBusy(false); }
  }

  return (
    <div className="space-y-3 text-sm">
      <label className="block font-medium text-slate-700">Photo of your meal
        <input type="file" disabled={busy} accept="image/jpeg,image/png,image/webp" capture="environment" onChange={(e) => pick(e.target.files?.[0])}
          className="mt-1 block w-full text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:font-semibold file:text-indigo-800" />
      </label>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      {preview && <img src={preview} alt="Your meal" className="h-32 w-full rounded-lg object-cover" />}
      <label className="block font-medium text-slate-700">Your goal
        <select disabled={busy} value={goal} onChange={(e) => setGoal(e.target.value as Goal)}
          className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 capitalize">
          {GOALS.map((g) => <option key={g} value={g}>{g}</option>)}
        </select>
      </label>
      <button onClick={analyze} disabled={!file || busy}
        className="inline-flex items-center gap-2 rounded-lg bg-indigo-700 px-4 py-2 font-semibold text-white hover:bg-indigo-800 disabled:opacity-60">
        {busy ? <Loader2 size={16} className="animate-spin" aria-hidden /> : <Camera size={16} aria-hidden />}
        {busy ? "Analysing…" : "Analyse meal"}
      </button>
      {error && <p role="alert" className="text-red-700">{error}</p>}
      <div aria-live="polite">
        {result && (
          <div className="space-y-2 text-slate-800">
            <p className="text-2xl font-bold tabular-nums">{result.total_calories} kcal</p>
            <p className="text-slate-700">Protein {result.protein_g} g · Carbs {result.carbs_g} g · Fat {result.fat_g} g</p>
            <ul className="list-disc pl-5">{result.foods.map((f, i) => <li key={`${i}-${f.name}`}>{f.name}{f.grams ? ` (about ${f.grams} g)` : ""}: {f.calories} kcal</li>)}</ul>
            <p>{result.goal_advice}</p>
            <p className="flex items-center gap-1 font-semibold"><Dumbbell size={16} aria-hidden /> Workout for your goal</p>
            <ul className="list-disc pl-5">{result.workout_plan.map((w, i) => <li key={`${i}-${w.activity}`}>{w.activity}: {w.minutes} min (about {w.calories_burned} kcal)</li>)}</ul>
            <p className="text-xs text-slate-600">{result.disclaimer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
