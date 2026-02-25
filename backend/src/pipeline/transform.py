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
        "release_date": raw.get("album", {}).get("release_date"),
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


TAG_MOOD_MAP: dict[str, dict[str, float]] = {
    # energy
    "energetic": {"energy": 0.9}, "power": {"energy": 0.85}, "intense": {"energy": 0.9},
    "aggressive": {"energy": 0.95}, "hard": {"energy": 0.8},
    "chill": {"energy": 0.2, "valence": 0.5}, "mellow": {"energy": 0.2},
    "calm": {"energy": 0.15}, "ambient": {"energy": 0.1, "instrumentalness": 0.7},
    "relaxing": {"energy": 0.15, "valence": 0.5},
    # valence
    "happy": {"valence": 0.9, "energy": 0.7}, "upbeat": {"valence": 0.85, "energy": 0.75},
    "feel good": {"valence": 0.9}, "uplifting": {"valence": 0.85},
    "sad": {"valence": 0.1, "energy": 0.25}, "melancholy": {"valence": 0.15},
    "dark": {"valence": 0.1, "energy": 0.5}, "depressing": {"valence": 0.05},
    # danceability
    "dance": {"danceability": 0.9, "energy": 0.7}, "party": {"danceability": 0.9, "energy": 0.85},
    "groovy": {"danceability": 0.85}, "funky": {"danceability": 0.85, "energy": 0.7},
    "club": {"danceability": 0.9, "energy": 0.8},
    # acousticness
    "acoustic": {"acousticness": 0.9}, "folk": {"acousticness": 0.7},
    "unplugged": {"acousticness": 0.85},
    # instrumentalness
    "instrumental": {"instrumentalness": 0.9}, "post-rock": {"instrumentalness": 0.6},
    # speechiness
    "rap": {"speechiness": 0.8}, "hip-hop": {"speechiness": 0.7},
    "spoken word": {"speechiness": 0.9},
    # liveness
    "live": {"liveness": 0.9}, "concert": {"liveness": 0.85},
}


def transform_lastfm_tags(track_id: str, raw: dict) -> dict:
    """Convert Last.fm API response to a DB row dict."""
    tags = []
    for tag in raw.get("toptags", {}).get("tag", []):
        tags.append({"name": tag.get("name", ""), "count": int(tag.get("count", 0))})
    return {
        "track_id": track_id,
        "tags": json.dumps(tags),
        "global_listeners": None,
        "global_playcount": None,
    }


def derive_mood_features_from_tags(track_id: str, tags_json: str) -> dict | None:
    """Map Last.fm tags to AudioFeature-compatible scores (0.0-1.0)."""
    tags = json.loads(tags_json) if isinstance(tags_json, str) else tags_json
    if not tags:
        return None

    feature_sums: dict[str, float] = {
        "danceability": 0, "energy": 0, "valence": 0, "acousticness": 0,
        "instrumentalness": 0, "speechiness": 0, "liveness": 0,
    }
    feature_weights: dict[str, float] = {k: 0 for k in feature_sums}

    for tag in tags:
        name = tag.get("name", "").lower().strip()
        count = max(int(tag.get("count", 0)), 1)
        if name in TAG_MOOD_MAP:
            for feat, score in TAG_MOOD_MAP[name].items():
                if feat in feature_sums:
                    feature_sums[feat] += score * count
                    feature_weights[feat] += count

    # Only produce a result if we matched at least one tag
    if not any(w > 0 for w in feature_weights.values()):
        return None

    result = {"track_id": track_id}
    for feat in feature_sums:
        if feature_weights[feat] > 0:
            result[feat] = round(feature_sums[feat] / feature_weights[feat], 3)
        else:
            result[feat] = 0.5  # neutral default
    # Fill non-tag fields with defaults
    result["tempo"] = None
    result["loudness"] = None
    result["key"] = None
    result["mode"] = None
    result["time_signature"] = None
    return result


def _first_image(images: list[dict] | None) -> str | None:
    if images:
        return images[0].get("url")
    return None
