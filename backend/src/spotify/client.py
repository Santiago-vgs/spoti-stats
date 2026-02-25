import spotipy
from spotipy.exceptions import SpotifyException

from src.spotify.auth import get_spotify_client


class SpotifyWrapper:
    def __init__(self, client: spotipy.Spotify | None = None):
        self.sp = client or get_spotify_client()

    def get_recently_played(self, limit: int = 50) -> list[dict]:
        results = self.sp.current_user_recently_played(limit=limit)
        return results.get("items", [])

    def get_top_tracks(self, time_range: str = "medium_term", limit: int = 50) -> list[dict]:
        results = self.sp.current_user_top_tracks(limit=limit, time_range=time_range)
        return results.get("items", [])

    def get_top_artists(self, time_range: str = "medium_term", limit: int = 50) -> list[dict]:
        results = self.sp.current_user_top_artists(limit=limit, time_range=time_range)
        return results.get("items", [])

    def get_playlists(self, limit: int = 50) -> list[dict]:
        results = self.sp.current_user_playlists(limit=limit)
        return results.get("items", [])

    def get_playlist_tracks(self, playlist_id: str) -> list[dict]:
        tracks = []
        results = self.sp.playlist_items(playlist_id, limit=100)
        tracks.extend(results.get("items", []))
        while results.get("next"):
            results = self.sp.next(results)
            tracks.extend(results.get("items", []))
        return tracks

    def get_audio_features(self, track_ids: list[str]) -> list[dict]:
        """Fetch audio features in batches of 100. Returns empty list if API is unavailable (deprecated)."""
        results = []
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i : i + 100]
            try:
                features = self.sp.audio_features(batch)
                results.extend(f for f in features if f is not None)
            except SpotifyException as e:
                if e.http_status == 403:
                    print("  Audio features API returned 403 (likely deprecated). Skipping.")
                    return results
                raise
        return results

    def get_recently_played_after(self, after_ms: int, limit: int = 50) -> list[dict]:
        """Fetch recently played tracks after a timestamp (ms since epoch)."""
        results = self.sp.current_user_recently_played(limit=limit, after=after_ms)
        return results.get("items", [])
