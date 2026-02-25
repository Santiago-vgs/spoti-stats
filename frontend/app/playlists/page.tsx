"use client";

import { useState } from "react";
import useSWR from "swr";
import { fetcher, apiFetch } from "@/lib/api";
import { Playlist, PlaylistTrack } from "@/lib/types";
import Card from "@/components/ui/Card";
import { ListItemSkeleton } from "@/components/ui/Skeleton";

export default function PlaylistsPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const { data: playlists } = useSWR<Playlist[]>(
    "/playlists",
    fetcher("/playlists")
  );

  const { data: tracks, isLoading: tracksLoading } = useSWR<PlaylistTrack[]>(
    selectedId ? `/playlists/${selectedId}/tracks` : null,
    (key: string) => apiFetch<PlaylistTrack[]>(key)
  );

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Playlists</h1>

      {!playlists || playlists.length === 0 ? (
        <Card>
          <p className="text-zinc-400">
            No playlists yet. Click <strong className="text-green-500">Sync Data</strong> in the navbar to load them.
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto pr-1">
            {playlists.map((pl) => (
              <button
                key={pl.id}
                onClick={() => setSelectedId(pl.id)}
                aria-selected={selectedId === pl.id}
                className={`w-full text-left p-4 rounded-xl border transition-colors ${
                  selectedId === pl.id
                    ? "bg-zinc-800 border-green-600"
                    : "bg-zinc-900 border-zinc-800 hover:border-zinc-700"
                }`}
              >
                <div className="flex items-center gap-3">
                  {pl.image_url && (
                    <img src={pl.image_url} alt="" className="w-12 h-12 rounded" />
                  )}
                  <div className="min-w-0">
                    <p className="font-medium truncate">{pl.name}</p>
                    <p className="text-sm text-zinc-400">
                      {pl.total_tracks} tracks
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="lg:col-span-2">
            {selectedId ? (
              <Card>
                <h2 className="text-lg font-semibold mb-4">
                  {playlists.find((p) => p.id === selectedId)?.name}
                </h2>
                {tracksLoading ? (
                  <div className="space-y-1">
                    {Array.from({ length: 8 }).map((_, i) => (
                      <ListItemSkeleton key={i} />
                    ))}
                  </div>
                ) : tracks && tracks.length > 0 ? (
                  <div className="space-y-2">
                    {tracks.map((pt, i) => (
                      <div
                        key={`${pt.track_id}-${i}`}
                        className="flex items-center gap-3 p-2 rounded-lg hover:bg-zinc-800/50 transition-colors"
                      >
                        <span className="text-zinc-400 font-mono text-sm w-6 text-right">
                          {(pt.position ?? i) + 1}
                        </span>
                        {pt.track?.album_image_url && (
                          <img
                            src={pt.track.album_image_url}
                            alt=""
                            className="w-8 h-8 rounded"
                          />
                        )}
                        <div className="min-w-0 flex-1">
                          <p className="text-white truncate">
                            {pt.track?.name || pt.track_id}
                          </p>
                          <p className="text-sm text-zinc-400 truncate">
                            {pt.track?.artist_name}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-zinc-400">No tracks in this playlist.</p>
                )}
              </Card>
            ) : (
              <Card>
                <p className="text-zinc-400">Select a playlist to view tracks.</p>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
