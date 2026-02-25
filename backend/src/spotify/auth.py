import spotipy
from spotipy.oauth2 import SpotifyOAuth

from src.config import settings

SCOPES = [
    "user-read-recently-played",
    "user-top-read",
    "playlist-read-private",
    "playlist-read-collaborative",
]

_oauth_instance: SpotifyOAuth | None = None


def get_spotify_oauth() -> SpotifyOAuth:
    global _oauth_instance
    if _oauth_instance is None:
        _oauth_instance = SpotifyOAuth(
            client_id=settings.spotipy_client_id,
            client_secret=settings.spotipy_client_secret,
            redirect_uri=settings.spotipy_redirect_uri,
            scope=" ".join(SCOPES),
            cache_path=".spotify_cache",
        )
    return _oauth_instance


def get_auth_url() -> str:
    oauth = get_spotify_oauth()
    return oauth.get_authorize_url()


def exchange_code(code: str) -> dict:
    oauth = get_spotify_oauth()
    token_info = oauth.get_access_token(code, as_dict=True)
    return token_info


def is_authenticated() -> bool:
    oauth = get_spotify_oauth()
    token_info = oauth.get_cached_token()
    if token_info is None:
        return False
    if oauth.is_token_expired(token_info):
        try:
            oauth.refresh_access_token(token_info["refresh_token"])
            return True
        except Exception:
            return False
    return True


def get_spotify_client() -> spotipy.Spotify:
    auth_manager = get_spotify_oauth()
    return spotipy.Spotify(auth_manager=auth_manager)
