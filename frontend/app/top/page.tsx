"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { TopItem, GenreCount } from "@/lib/types";
import Card from "@/components/ui/Card";
import TimeRangeSelector from "@/components/ui/TimeRangeSelector";
import GenreDistribution from "@/components/charts/GenreDistribution";

export default function TopPage() {
  const [timeRange, setTimeRange] = useState("medium_term");

  const { data: topTracks } = useSWR<TopItem[]>(
    `/stats/top-tracks?time_range=${timeRange}&limit=20`,
    fetcher(`/stats/top-tracks?time_range=${timeRange}&limit=20`),
  );

  const { data: topArtists } = useSWR<TopItem[]>(
    `/stats/top-artists?time_range=${timeRange}&limit=20`,
    fetcher(`/stats/top-artists?time_range=${timeRange}&limit=20`),
  );

  const { data: genres } = useSWR<GenreCount[]>("/stats/genres", fetcher("/stats/genres"));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Top Tracks & Artists</h1>
        <TimeRangeSelector selected={timeRange} onChange={setTimeRange} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-lg font-semibold mb-4">Top Tracks</h2>
          {topTracks && topTracks.length > 0 ? (
            <div className="space-y-2">
              {topTracks.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
                >
                  <span className="text-zinc-500 font-mono text-sm w-6 text-right">
                    {item.rank}
                  </span>
                  {item.image_url && (
                    <img src={item.image_url} alt="" className="w-8 h-8 rounded" />
                  )}
                  <span className="text-white truncate">{item.item_name}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-zinc-500">No data yet.</p>
          )}
        </Card>

        <Card>
          <h2 className="text-lg font-semibold mb-4">Top Artists</h2>
          {topArtists && topArtists.length > 0 ? (
            <div className="space-y-2">
              {topArtists.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
                >
                  <span className="text-zinc-500 font-mono text-sm w-6 text-right">
                    {item.rank}
                  </span>
                  {item.image_url && (
                    <img src={item.image_url} alt="" className="w-8 h-8 rounded-full" />
                  )}
                  <span className="text-white truncate">{item.item_name}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-zinc-500">No data yet.</p>
          )}
        </Card>
      </div>

      <Card>
        <h2 className="text-lg font-semibold mb-4">Genre Distribution</h2>
        {genres && genres.length > 0 ? (
          <GenreDistribution data={genres} />
        ) : (
          <p className="text-zinc-500">No genre data yet.</p>
        )}
      </Card>
    </div>
  );
}
