"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { InsightItem } from "@/lib/types";
import Card from "./Card";

export default function InsightsCard() {
  const { data: insights } = useSWR<InsightItem[]>(
    "/insights?limit=3",
    fetcher("/insights?limit=3"),
  );

  if (!insights || insights.length === 0) return null;

  return (
    <Card>
      <h2 className="text-lg font-semibold mb-4">AI Insights</h2>
      <div className="space-y-3">
        {insights.map((insight) => (
          <div key={insight.id} className="flex gap-3 p-3 rounded-lg bg-zinc-800/50">
            <span className="text-green-500 text-lg mt-0.5">💡</span>
            <p className="text-sm text-zinc-300 leading-relaxed">{insight.content}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}
