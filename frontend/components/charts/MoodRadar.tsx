"use client";

import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { MoodCluster } from "@/lib/types";
import { CHART_TOOLTIP } from "@/lib/chartTheme";

const COLORS = ["#22c55e", "#3b82f6", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

const CLUSTER_NAMES = ["Chill", "Energetic", "Happy", "Dark", "Acoustic", "Vocal"];

interface Props {
  data: MoodCluster[];
}

export default function MoodRadar({ data }: Props) {
  // Transform cluster data into radar-compatible format
  const features = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "instrumentalness",
    "speechiness",
    "liveness",
  ] as const;

  const radarData = features.map((feature) => {
    const point: Record<string, string | number> = {
      feature: feature.charAt(0).toUpperCase() + feature.slice(1),
    };
    data.forEach((cluster, i) => {
      point[`cluster_${i}`] = cluster.features[feature];
    });
    return point;
  });

  return (
    <div>
      <ResponsiveContainer width="100%" height={350}>
        <RadarChart data={radarData}>
          <PolarGrid stroke="#27272a" />
          <PolarAngleAxis dataKey="feature" tick={{ fontSize: 11, fill: "#a1a1aa" }} />
          <PolarRadiusAxis tick={false} axisLine={false} domain={[0, 1]} />
          <Tooltip contentStyle={CHART_TOOLTIP} />
          {data.map((cluster, i) => (
            <Radar
              key={cluster.cluster_id}
              name={`${CLUSTER_NAMES[i] || `Cluster ${i}`} (${cluster.count})`}
              dataKey={`cluster_${i}`}
              stroke={COLORS[i % COLORS.length]}
              fill={COLORS[i % COLORS.length]}
              fillOpacity={0.1}
              strokeWidth={2}
            />
          ))}
        </RadarChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-3 mt-3 justify-center">
        {data.map((cluster, i) => (
          <div key={cluster.cluster_id} className="flex items-center gap-1.5 text-xs text-zinc-400">
            <div
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            />
            {CLUSTER_NAMES[i] || `Cluster ${i}`} ({cluster.count})
          </div>
        ))}
      </div>
      <p className="text-center text-[10px] text-zinc-600 mt-2">Powered by Last.fm tags</p>
    </div>
  );
}
