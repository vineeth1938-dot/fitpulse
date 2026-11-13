import { CheckCircle2, AlertTriangle, Flame, TrendingDown } from "lucide-react";
import type { Risk } from "./api";

export const RISK: Record<Risk, { color: string; badge: string; Icon: typeof Flame; hint: string }> = {
  Safe: { color: "#16a34a", badge: "bg-green-100 text-green-800", Icon: CheckCircle2, hint: "0.80 – 1.30" },
  Caution: { color: "#d97706", badge: "bg-amber-100 text-amber-800", Icon: AlertTriangle, hint: "1.31 – 1.50" },
  Danger: { color: "#dc2626", badge: "bg-red-100 text-red-800", Icon: Flame, hint: "above 1.50" },
  Undertraining: { color: "#64748b", badge: "bg-slate-200 text-slate-700", Icon: TrendingDown, hint: "below 0.80" },
};
