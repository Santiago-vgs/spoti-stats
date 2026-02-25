"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { DecadeStat } from "@/lib/types";
import Card from "@/components/ui/Card";
import DecadeChart from "@/components/charts/DecadeChart";

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

export default function DecadesPage() {
  const { data: decades, isLoading } = useSWR<DecadeStat[]>("/decades", fetcher("/decades"));

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Decadeology</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 animate-pulse h-48"
            />
          ))}
        </div>
      </div>
    );
  }

  if (!decades || decades.length === 0) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold">Decadeology</h1>
        <Card>
          <p className="text-zinc-500">No decade data yet. Sync your listening history first.</p>
        </Card>
      </div>
    );
  }

  // The first item has the most plays (API sorts by total_plays desc)
  const dominant = decades[0];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Decadeology</h1>

      {/* Hero: dominant decade */}
      <Card className="border-green-500/40">
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <p className="text-sm text-zinc-400 mb-1">Your dominant era</p>
            <h2
              className="text-4xl font-bold"
              style={{ color: DECADE_COLORS[dominant.decade] || "#22c55e" }}
            >
              {dominant.decade}
            </h2>
            <p className="text-zinc-300 mt-2 text-lg">{dominant.insight}</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-white">{dominant.percentage}%</p>
            <p className="text-sm text-zinc-500">{dominant.total_plays.toLocaleString()} plays</p>
          </div>
        </div>
      </Card>

      {/* Bar chart */}
      <Card>
        <h2 className="text-lg font-semibold mb-4">Plays by Decade</h2>
        <DecadeChart data={decades} />
      </Card>

      {/* Per-decade cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {decades.map((d) => (
          <Card key={d.decade}>
            <div className="flex items-center justify-between mb-3">
              <h3
                className="text-xl font-bold"
                style={{ color: DECADE_COLORS[d.decade] || "#a1a1aa" }}
              >
                {d.decade}
              </h3>
              <span className="text-sm text-zinc-500">
                {d.percentage}% &middot; {d.total_plays.toLocaleString()} plays
              </span>
            </div>
            <p className="text-zinc-400 text-sm mb-4 italic">{d.insight}</p>

            <div className="grid grid-cols-2 gap-4">
              {/* Top Artists */}
              <div>
                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                  Top Artists
                </h4>
                <div className="space-y-1.5">
                  {d.top_artists.map((a, i) => (
                    <div key={a.name} className="flex items-center gap-2 text-sm">
                      <span className="text-zinc-600 font-mono text-xs w-4">{i + 1}</span>
                      <span className="text-zinc-300 truncate">{a.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top Tracks */}
              <div>
                <h4 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2">
                  Top Tracks
                </h4>
                <div className="space-y-1.5">
                  {d.top_tracks.map((t, i) => (
                    <div key={`${t.name}-${i}`} className="flex items-center gap-2 text-sm">
                      <span className="text-zinc-600 font-mono text-xs w-4">{i + 1}</span>
                      {t.image_url && <img src={t.image_url} alt="" className="w-5 h-5 rounded" />}
                      <span className="text-zinc-300 truncate">{t.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
