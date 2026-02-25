"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { GenreCount } from "@/lib/types";
import { CHART_TOOLTIP } from "@/lib/chartTheme";

const COLORS = [
  "#22c55e",
  "#3b82f6",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#ec4899",
  "#14b8a6",
  "#f97316",
  "#06b6d4",
  "#84cc16",
  "#e879f9",
  "#fb923c",
  "#2dd4bf",
  "#a78bfa",
  "#fbbf24",
];

interface Props {
  data: GenreCount[];
}

export default function GenreDistribution({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={Math.max(300, data.length * 32)}>
      <BarChart data={data} layout="vertical" barCategoryGap="20%">
        <XAxis type="number" stroke="#71717a" tick={{ fontSize: 12 }} />
        <YAxis
          dataKey="genre"
          type="category"
          stroke="#71717a"
          tick={{ fontSize: 12 }}
          width={140}
        />
        <Tooltip
          contentStyle={CHART_TOOLTIP}
          labelStyle={{ color: "#a1a1aa" }}
          formatter={(value) => [`${value} artists`, "Count"]}
        />
        <Bar dataKey="count" radius={[0, 6, 6, 0]} animationDuration={800}>
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
