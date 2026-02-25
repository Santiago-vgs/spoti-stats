"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LabelList,
} from "recharts";
import { DecadeStat } from "@/lib/types";
import { CHART_TOOLTIP } from "@/lib/chartTheme";

const DECADE_COLORS: Record<string, string> = {
  "1950s": "#f97316",
  "1960s": "#f59e0b",
  "1970s": "#eab308",
  "1980s": "#84cc16",
  "1990s": "#22c55e",
  "2000s": "#14b8a6",
  "2010s": "#3b82f6",
  "2020s": "#8b5cf6",
};

function getColor(decade: string): string {
  return DECADE_COLORS[decade] || "#6b7280";
}

interface Props {
  data: DecadeStat[];
}

export default function DecadeChart({ data }: Props) {
  const sorted = [...data].sort((a, b) => {
    const aYear = parseInt(a.decade);
    const bYear = parseInt(b.decade);
    return aYear - bYear;
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={sorted} margin={{ top: 20, right: 20, bottom: 5, left: 0 }}>
        <XAxis
          dataKey="decade"
          tick={{ fontSize: 12, fill: "#a1a1aa" }}
          axisLine={{ stroke: "#27272a" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 11, fill: "#71717a" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={CHART_TOOLTIP}
          formatter={(value: number) => [`${value} plays`, "Plays"]}
        />
        <Bar dataKey="total_plays" radius={[6, 6, 0, 0]}>
          {sorted.map((entry) => (
            <Cell key={entry.decade} fill={getColor(entry.decade)} />
          ))}
          <LabelList
            dataKey="percentage"
            position="top"
            formatter={(v: number) => `${v}%`}
            style={{ fontSize: 11, fill: "#a1a1aa" }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
