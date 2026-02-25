"""Last.fm API client for fetching track tags."""

import time

import requests

LASTFM_API_BASE = "https://ws.audioscrobbler.com/2.0/"


class LastfmClient:
    def __init__(self, api_key: str, delay: float = 0.2):
        self.api_key = api_key
        self.delay = delay

    def get_top_tags(self, artist: str, track: str) -> dict:
        """Fetch top tags for a track from Last.fm.

        Returns the raw API response dict, or an empty dict on error/404.
        """
        params = {
            "method": "track.getTopTags",
            "artist": artist,
            "track": track,
            "api_key": self.api_key,
            "format": "json",
        }
        try:
            time.sleep(self.delay)
            resp = requests.get(LASTFM_API_BASE, params=params, timeout=10)
            if resp.status_code == 404:
                return {}
            resp.raise_for_status()
            data = resp.json()
            # Last.fm returns {"error": 6, ...} for not-found tracks
            if "error" in data:
                return {}
            return data
        except (requests.RequestException, ValueError):
            return {}
