"use client";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { TrendPoint } from "@/lib/api";

export function CorridorChart({ data }: { data: TrendPoint[] }) {
  return (
    <div role="img" aria-label="28-day acute versus chronic load chart" className="h-64 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tickFormatter={(d: string) => d.slice(5)} fontSize={12} interval={3} />
          <YAxis fontSize={12} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="acute_load" name="Acute (7-day)" stroke="#dc2626" strokeWidth={2.5} dot={false} />
          <Line type="monotone" dataKey="chronic_load" name="Chronic (28-day)" stroke="#0f766e" strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
