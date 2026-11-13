import type { Athlete } from "@/lib/api";
import { RISK } from "@/lib/risk";

export function AthleteCard({ a, selected, onSelect }: { a: Athlete; selected: boolean; onSelect: () => void }) {
  const r = RISK[a.risk_status];
  return (
    <button
      onClick={onSelect}
      aria-pressed={selected}
      className={`w-full rounded-xl border bg-white p-4 text-left shadow-sm transition hover:shadow-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-indigo-600 ${
        selected ? "border-indigo-600 ring-2 ring-indigo-200" : "border-slate-200"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="font-semibold text-slate-900">{a.name}</p>
          <p className="text-sm text-slate-600">{[a.sport, a.position].filter(Boolean).join(" · ")}</p>
        </div>
        <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${r.badge}`}>
          <r.Icon size={14} aria-hidden /> {a.risk_status}
        </span>
      </div>
      <p className="mt-3 text-4xl font-bold tabular-nums" style={{ color: r.color }}>{a.acwr.toFixed(2)}</p>
      <p className="text-xs text-slate-600">ACWR · acute {a.acute_load} / chronic {a.chronic_load}</p>
    </button>
  );
}
