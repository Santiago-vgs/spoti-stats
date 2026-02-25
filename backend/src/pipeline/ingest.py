from concurrent.futures import ThreadPoolExecutor

from spotipy.exceptions import SpotifyException

from src.spotify.client import SpotifyWrapper

TIME_RANGES = ["short_term", "medium_term", "long_term"]


def ingest_recently_played(wrapper: SpotifyWrapper, after_ms: int | None = None) -> list[dict]:
    if after_ms:
        return wrapper.get_recently_played_after(after_ms=after_ms, limit=50)
    return wrapper.get_recently_played(limit=50)


def ingest_top_tracks(wrapper: SpotifyWrapper) -> dict[str, list[dict]]:
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {tr: pool.submit(wrapper.get_top_tracks, time_range=tr, limit=50) for tr in TIME_RANGES}
        return {tr: f.result() for tr, f in futures.items()}


def ingest_top_artists(wrapper: SpotifyWrapper) -> dict[str, list[dict]]:
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {tr: pool.submit(wrapper.get_top_artists, time_range=tr, limit=50) for tr in TIME_RANGES}
        return {tr: f.result() for tr, f in futures.items()}


def ingest_playlists(wrapper: SpotifyWrapper) -> list[dict]:
    playlists = wrapper.get_playlists(limit=50)

    def _fetch_tracks(pl: dict) -> list[dict]:
        try:
            return wrapper.get_playlist_tracks(pl["id"])
        except SpotifyException as e:
            print(f"  Skipping playlist '{pl.get('name', pl['id'])}': {e.http_status} {e.reason}")
            return []

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pl["id"]: pool.submit(_fetch_tracks, pl) for pl in playlists}
        for pl in playlists:
            pl["_tracks"] = futures[pl["id"]].result()

    return playlists


def ingest_audio_features(wrapper: SpotifyWrapper, track_ids: list[str]) -> list[dict]:
    return wrapper.get_audio_features(track_ids)
