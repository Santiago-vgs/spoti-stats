export interface Track {
  id: string;
  name: string;
  artist_name: string | null;
  album_name: string | null;
  album_image_url: string | null;
  duration_ms: number | null;
  popularity: number | null;
  spotify_url: string | null;
}

export interface HistoryItem {
  id: number;
  track_id: string;
  played_at: string;
  context_type: string | null;
  track: Track | null;
}

export interface TopItem {
  id: number;
  item_type: string;
  item_id: string;
  item_name: string;
  time_range: string;
  rank: number;
  snapshot_date: string;
  image_url: string | null;
  extra_data: string;
}

export interface OverviewStats {
  total_plays: number;
  unique_tracks: number;
  unique_artists: number;
  total_listening_ms: number;
  top_artist: string | null;
  top_track: string | null;
}

export interface GenreCount {
  genre: string;
  count: number;
}

export interface TimelinePoint {
  date: string;
  plays: number;
}

export interface Playlist {
  id: string;
  name: string;
  description: string | null;
  owner_name: string | null;
  image_url: string | null;
  total_tracks: number | null;
  spotify_url: string | null;
}

export interface PlaylistTrack {
  track_id: string;
  added_at: string | null;
  position: number | null;
  track: Track | null;
}

export interface Artist {
  id: string;
  name: string;
  genres: string;
  popularity: number | null;
  image_url: string | null;
  spotify_url: string | null;
}

export interface AuthStatus {
  authenticated: boolean;
}

export interface PipelineResult {
  status: string;
  message: string;
}

// --- New types for AI & Data features ---

export interface InsightItem {
  id: number;
  content: string;
  insight_type: string;
  generated_at: string | null;
}

export interface MoodCluster {
  cluster_id: number;
  count: number;
  features: {
    danceability: number;
    energy: number;
    valence: number;
    acousticness: number;
    instrumentalness: number;
    speechiness: number;
    liveness: number;
  };
}

export interface HeatmapCell {
  day_of_week: number;
  hour: number;
  play_count: number;
}

export interface DecadeTopTrack {
  name: string;
  artist_name: string;
  plays: number;
  image_url: string | null;
}

export interface DecadeTopArtist {
  name: string;
  plays: number;
}

export interface DecadeStat {
  decade: string;
  total_plays: number;
  percentage: number;
  insight: string;
  top_tracks: DecadeTopTrack[];
  top_artists: DecadeTopArtist[];
}

export interface DailySummary {
  date: string;
  total_plays: number;
  total_duration_ms: number;
  unique_tracks: number;
  unique_artists: number;
  avg_energy: number | null;
  avg_valence: number | null;
  avg_danceability: number | null;
}
