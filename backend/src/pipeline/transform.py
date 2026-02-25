import json
from datetime import date, datetime


def transform_artist(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "name": raw["name"],
        "genres": json.dumps(raw.get("genres", [])),
        "popularity": raw.get("popularity"),
        "image_url": _first_image(raw.get("images")),
        "spotify_url": raw.get("external_urls", {}).get("spotify"),
    }


def transform_track(raw: dict) -> dict:
    artists = raw.get("artists", [])
    return {
        "id": raw["id"],
        "name": raw["name"],
        "artist_name": ", ".join(a["name"] for a in artists),
        "album_name": raw.get("album", {}).get("name"),
        "album_image_url": _first_image(raw.get("album", {}).get("images")),
        "duration_ms": raw.get("duration_ms"),
        "popularity": raw.get("popularity"),
        "spotify_url": raw.get("external_urls", {}).get("spotify"),
        "preview_url": raw.get("preview_url"),
        "_artist_ids": [a["id"] for a in artists],
        "_artists_raw": artists,
    }


def transform_recently_played(items: list[dict]) -> list[dict]:
    results = []
    for item in items:
        track_data = transform_track(item["track"])
        results.append({
            "track": track_data,
            "played_at": datetime.fromisoformat(item["played_at"].replace("Z", "+00:00")),
            "context_type": (item.get("context") or {}).get("type"),
        })
    return results


def transform_top_items(
    items: list[dict], item_type: str, time_range: str
) -> list[dict]:
    snapshot = date.today().isoformat()
    results = []
    for rank, item in enumerate(items, 1):
        results.append({
            "item_type": item_type,
            "item_id": item["id"],
            "item_name": item["name"],
            "time_range": time_range,
            "rank": rank,
            "snapshot_date": snapshot,
            "image_url": _first_image(item.get("images") or item.get("album", {}).get("images")),
            "extra_data": json.dumps({
                "popularity": item.get("popularity"),
                "genres": item.get("genres", []),
            }),
        })
    return results


def transform_playlist(raw: dict) -> dict:
    return {
        "id": raw["id"],
        "name": raw["name"],
        "description": raw.get("description", ""),
        "owner_name": raw.get("owner", {}).get("display_name"),
        "image_url": _first_image(raw.get("images")),
        "total_tracks": raw.get("tracks", {}).get("total", 0),
        "spotify_url": raw.get("external_urls", {}).get("spotify"),
        "snapshot_id": raw.get("snapshot_id"),
    }


def transform_playlist_tracks(items: list[dict], playlist_id: str) -> list[dict]:
    results = []
    for pos, item in enumerate(items):
        track = item.get("track")
        if not track or not track.get("id"):
            continue
        results.append({
            "playlist_id": playlist_id,
            "track_id": track["id"],
            "added_at": (
                datetime.fromisoformat(item["added_at"].replace("Z", "+00:00"))
                if item.get("added_at")
                else None
            ),
            "position": pos,
            "_track_raw": track,
        })
    return results


def transform_audio_features(raw_features: list[dict]) -> list[dict]:
    results = []
    for f in raw_features:
        if not f or not f.get("id"):
            continue
        results.append({
            "track_id": f["id"],
            "danceability": f.get("danceability"),
            "energy": f.get("energy"),
            "valence": f.get("valence"),
            "tempo": f.get("tempo"),
            "acousticness": f.get("acousticness"),
            "instrumentalness": f.get("instrumentalness"),
            "speechiness": f.get("speechiness"),
            "liveness": f.get("liveness"),
            "loudness": f.get("loudness"),
            "key": f.get("key"),
            "mode": f.get("mode"),
            "time_signature": f.get("time_signature"),
        })
    return results


def _first_image(images: list[dict] | None) -> str | None:
    if images:
        return images[0].get("url")
    return None
