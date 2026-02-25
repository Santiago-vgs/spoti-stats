import urllib.parse

import requests
from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.config import settings
from src.spotify.auth import exchange_code, get_auth_url, is_authenticated

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
def login():
    url = get_auth_url()
    return RedirectResponse(url)


@router.get("/status")
def status():
    return {"authenticated": is_authenticated()}


@router.get("/test")
def test_credentials():
    """Hit Spotify's token endpoint with client_credentials to verify the ID/secret work."""
    cid = settings.spotipy_client_id
    secret = settings.spotipy_client_secret
    redirect = settings.spotipy_redirect_uri

    # Test 1: Are credentials set?
    if not cid or not secret:
        return {"ok": False, "error": "client_id or client_secret is empty in .env"}

    # Test 2: Do they work with Spotify?
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(cid, secret),
    )

    if resp.status_code != 200:
        return {
            "ok": False,
            "error": f"Spotify rejected credentials: {resp.status_code} {resp.text}",
            "client_id_preview": cid[:8] + "...",
        }

    # Test 3: Show the full auth URL so user can inspect
    auth_url = get_auth_url()
    parsed = urllib.parse.urlparse(auth_url)
    params = urllib.parse.parse_qs(parsed.query)

    return {
        "ok": True,
        "message": "Credentials are valid!",
        "redirect_uri_in_url": params.get("redirect_uri", [""])[0],
        "redirect_uri_in_config": redirect,
        "full_auth_url": auth_url,
    }
