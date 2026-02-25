"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { TopItem } from "@/lib/types";
import { CHART_TOOLTIP } from "@/lib/chartTheme";

interface Props {
  data: TopItem[];
}

export default function TopArtistsBar({ data }: Props) {
  // Use inverse rank as score so #1 gets the longest bar
  const maxRank = data.length;
  const chartData = data.slice(0, 10).map((item) => ({
    name: item.item_name.length > 18 ? item.item_name.slice(0, 18) + "..." : item.item_name,
    score: maxRank - item.rank + 1,
    fullName: item.item_name,
    rank: item.rank,
  }));

  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={chartData} layout="vertical" barCategoryGap="20%">
        <XAxis type="number" hide />
        <YAxis
          dataKey="name"
          type="category"
          stroke="#71717a"
          tick={{ fontSize: 12 }}
          width={140}
        />
        <Tooltip
          contentStyle={CHART_TOOLTIP}
          labelStyle={{ color: "#a1a1aa" }}
          formatter={(_, __, props) => [`#${props.payload.rank}`, props.payload.fullName]}
        />
        <Bar
          dataKey="score"
          fill="#22c55e"
          radius={[0, 6, 6, 0]}
          animationDuration={800}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}
