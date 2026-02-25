"use client";

import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { OverviewStats, TimelinePoint, TopItem, MoodCluster, HeatmapCell } from "@/lib/types";
import StatCard from "@/components/ui/StatCard";
import Card from "@/components/ui/Card";
import InsightsCard from "@/components/ui/InsightsCard";
import ListeningTimeline from "@/components/charts/ListeningTimeline";
import TopArtistsBar from "@/components/charts/TopArtistsBar";
import MoodRadar from "@/components/charts/MoodRadar";
import ListeningHeatmap from "@/components/charts/ListeningHeatmap";
import { DashboardSkeleton } from "@/components/ui/Skeleton";

function formatMs(ms: number): string {
  const hours = Math.floor(ms / 3_600_000);
  const minutes = Math.floor((ms % 3_600_000) / 60_000);
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes}m`;
}

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useSWR<OverviewStats>(
    "/stats/overview",
    fetcher("/stats/overview"),
  );
  const { data: timeline } = useSWR<TimelinePoint[]>(
    "/stats/listening-timeline?days=30",
    fetcher("/stats/listening-timeline?days=30"),
  );
  const { data: topArtists } = useSWR<TopItem[]>(
    "/stats/top-artists?time_range=medium_term&limit=10",
    fetcher("/stats/top-artists?time_range=medium_term&limit=10"),
  );
  const { data: moodClusters } = useSWR<MoodCluster[]>(
    "/insights/mood-profile",
    fetcher("/insights/mood-profile"),
  );
  const { data: heatmap } = useSWR<HeatmapCell[]>(
    "/insights/heatmap",
    fetcher("/insights/heatmap"),
  );

  if (statsLoading) {
    return <DashboardSkeleton />;
  }

  const hasData = stats && stats.total_plays > 0;

  if (!hasData) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-6">
        <div className="text-center space-y-3">
          <div className="text-5xl">🎧</div>
          <h1 className="text-3xl font-bold">Welcome to Spoti Stats</h1>
          <p className="text-zinc-400 max-w-md">
            Click <strong className="text-green-500">Sync Data</strong> in the navbar to pull your
            Spotify listening history and start exploring your stats.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard title="Total Plays" value={stats.total_plays} />
        <StatCard title="Unique Tracks" value={stats.unique_tracks} />
        <StatCard title="Unique Artists" value={stats.unique_artists} />
        <StatCard title="Listening Time" value={formatMs(stats.total_listening_ms)} />
        <StatCard title="Top Artist" value={stats.top_artist || "—"} />
        <StatCard title="Top Track" value={stats.top_track || "—"} />
      </div>

      {/* AI Insights */}
      <InsightsCard />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-lg font-semibold mb-4">Listening Activity (30 days)</h2>
          {timeline && timeline.length > 0 ? (
            <ListeningTimeline data={timeline} />
          ) : (
            <p className="text-zinc-400">No listening data for this period.</p>
          )}
        </Card>

        <Card>
          <h2 className="text-lg font-semibold mb-4">Top Artists (6 months)</h2>
          {topArtists && topArtists.length > 0 ? (
            <TopArtistsBar data={topArtists} />
          ) : (
            <p className="text-zinc-400">No top artist data yet.</p>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {moodClusters && moodClusters.length > 0 && (
          <Card>
            <h2 className="text-lg font-semibold mb-4">Mood Profile</h2>
            <MoodRadar data={moodClusters} />
          </Card>
        )}

        {heatmap && heatmap.length > 0 && (
          <Card>
            <h2 className="text-lg font-semibold mb-4">Listening Patterns</h2>
            <ListeningHeatmap data={heatmap} />
          </Card>
        )}
      </div>
    </div>
  );
}
