"use client";

import { useState } from "react";
import useSWR from "swr";
import { apiFetch } from "@/lib/api";
import { HistoryItem } from "@/lib/types";
import Card from "@/components/ui/Card";
import { ListItemSkeleton } from "@/components/ui/Skeleton";

export default function HistoryPage() {
  const [page, setPage] = useState(0);
  const limit = 50;

  const { data, isLoading } = useSWR<HistoryItem[]>(
    `/history?limit=${limit}&offset=${page * limit}`,
    () => apiFetch<HistoryItem[]>(`/history`, { limit: String(limit), offset: String(page * limit) })
  );

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Listening History</h1>

      <Card>
        {isLoading ? (
          <div className="space-y-1">
            {Array.from({ length: 10 }).map((_, i) => (
              <ListItemSkeleton key={i} />
            ))}
          </div>
        ) : data && data.length > 0 ? (
          <div className="space-y-2">
            {data.map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-4 p-3 rounded-lg hover:bg-zinc-800/50 transition-colors"
              >
                {item.track?.album_image_url && (
                  <img
                    src={item.track.album_image_url}
                    alt=""
                    className="w-10 h-10 rounded"
                  />
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white font-medium truncate">
                    {item.track?.name || item.track_id}
                  </p>
                  <p className="text-sm text-zinc-400 truncate">
                    {item.track?.artist_name} — {item.track?.album_name}
                  </p>
                </div>
                <div className="text-sm text-zinc-400 whitespace-nowrap">
                  {new Date(item.played_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-zinc-400">
            No history data yet. Click <strong className="text-green-500">Sync Data</strong> to get started.
          </p>
        )}
      </Card>

      <div className="flex justify-center gap-4">
        <button
          onClick={() => setPage(Math.max(0, page - 1))}
          disabled={page === 0}
          className="px-4 py-2 bg-zinc-800 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-700 transition-colors"
        >
          Previous
        </button>
        <span className="px-4 py-2 text-sm text-zinc-400">Page {page + 1}</span>
        <button
          onClick={() => setPage(page + 1)}
          disabled={!data || data.length < limit}
          className="px-4 py-2 bg-zinc-800 rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-zinc-700 transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
}
