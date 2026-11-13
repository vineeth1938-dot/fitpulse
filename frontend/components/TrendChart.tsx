"use client";
import { CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TrendPoint } from "@/lib/api";

export function TrendChart({ data }: { data: TrendPoint[] }) {
  const max = Math.max(2, ...data.map((d) => d.acwr ?? 0)) + 0.2;
  return (
    <div role="img" aria-label="28-day ACWR trend chart" className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -12 }}>
          <ReferenceArea y1={0.8} y2={1.3} fill="#16a34a" fillOpacity={0.1} />
          <ReferenceArea y1={1.3} y2={1.5} fill="#d97706" fillOpacity={0.12} />
          <ReferenceArea y1={1.5} y2={max} fill="#dc2626" fillOpacity={0.1} />
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tickFormatter={(d: string) => d.slice(5)} fontSize={12} interval={3} />
          <YAxis domain={[0, max]} fontSize={12} />
          <Tooltip />
          <Line type="monotone" dataKey="acwr" name="ACWR" stroke="#4338ca" strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
