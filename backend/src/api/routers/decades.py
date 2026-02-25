"""Decades breakdown endpoint — classifies listening by era."""

from collections import defaultdict

from fastapi import APIRouter
from sqlalchemy import func

from src.db.database import SessionLocal
from src.db.models import ListeningHistory, Track

router = APIRouter(tags=["decades"])


def _year_to_decade(year: int) -> str:
    decade_start = (year // 10) * 10
    return f"{decade_start}s"


def _generate_decade_insight(decade: str, pct: float) -> str:
    vibes = {
        "1950s": "a golden-era crooner",
        "1960s": "a flower-power dreamer",
        "1970s": "a groovy disco dancer",
        "1980s": "a synth-wave enthusiast",
        "1990s": "a grunge-era rebel",
        "2000s": "a Y2K pop lover",
        "2010s": "a streaming-age explorer",
        "2020s": "a modern music connoisseur",
    }
    vibe = vibes.get(decade, f"a {decade} aficionado")
    return f"You're {pct:.0f}% {vibe}"


@router.get("/decades")
def get_decades():
    session = SessionLocal()
    try:
        # Get all plays joined with track release_date
        rows = (
            session.query(
                Track.id,
                Track.name,
                Track.artist_name,
                Track.album_image_url,
                Track.release_date,
                func.count(ListeningHistory.id).label("plays"),
            )
            .join(ListeningHistory, ListeningHistory.track_id == Track.id)
            .filter(Track.release_date.isnot(None))
            .group_by(Track.id)
            .all()
        )

        if not rows:
            return []

        # Group by decade
        decade_data: dict[str, dict] = defaultdict(
            lambda: {
                "total_plays": 0,
                "tracks": [],  # (track_name, artist_name, plays, image_url)
                "artist_plays": defaultdict(int),
            }
        )

        total_plays = 0
        for row in rows:
            year_str = row.release_date[:4] if row.release_date else None
            if not year_str or not year_str.isdigit():
                continue
            year = int(year_str)
            if year < 1900 or year > 2099:
                continue
            decade = _year_to_decade(year)
            decade_data[decade]["total_plays"] += row.plays
            decade_data[decade]["tracks"].append(
                (row.name, row.artist_name, row.plays, row.album_image_url)
            )
            # Split artist_name to count each artist individually
            if row.artist_name:
                for artist in row.artist_name.split(", "):
                    decade_data[decade]["artist_plays"][artist.strip()] += row.plays
            total_plays += row.plays

        if total_plays == 0:
            return []

        result = []
        for decade in sorted(decade_data.keys()):
            info = decade_data[decade]
            pct = (info["total_plays"] / total_plays) * 100

            # Top 5 tracks by plays
            top_tracks = sorted(info["tracks"], key=lambda t: t[2], reverse=True)[:5]
            # Top 5 artists by plays
            top_artists = sorted(info["artist_plays"].items(), key=lambda a: a[1], reverse=True)[:5]

            result.append(
                {
                    "decade": decade,
                    "total_plays": info["total_plays"],
                    "percentage": round(pct, 1),
                    "insight": _generate_decade_insight(decade, pct),
                    "top_tracks": [
                        {"name": t[0], "artist_name": t[1], "plays": t[2], "image_url": t[3]}
                        for t in top_tracks
                    ],
                    "top_artists": [{"name": a[0], "plays": a[1]} for a in top_artists],
                }
            )

        # Sort by total plays descending
        result.sort(key=lambda d: d["total_plays"], reverse=True)
        return result
    finally:
        session.close()
