"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { TimelinePoint } from "@/lib/types";
import { CHART_TOOLTIP } from "@/lib/chartTheme";

interface Props {
  data: TimelinePoint[];
}

export default function ListeningTimeline({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="greenGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
        <XAxis
          dataKey="date"
          stroke="#71717a"
          tick={{ fontSize: 12 }}
          tickFormatter={(v) =>
            new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })
          }
          interval="preserveStartEnd"
        />
        <YAxis stroke="#71717a" tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={CHART_TOOLTIP}
          labelStyle={{ color: "#a1a1aa" }}
          itemStyle={{ color: "#22c55e" }}
        />
        <Area
          type="monotone"
          dataKey="plays"
          stroke="#22c55e"
          strokeWidth={2}
          fill="url(#greenGradient)"
          dot={false}
          animationDuration={800}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
