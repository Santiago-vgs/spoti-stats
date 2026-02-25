import json
import time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import GenreCount, OverviewStats, TopItemOut
from src.db.models import Artist, ListeningHistory, TopItem, Track

router = APIRouter(prefix="/stats", tags=["stats"])

# Simple TTL cache
_cache: dict[str, tuple[float, object]] = {}
CACHE_TTL = 60  # seconds


def _get_cached(key: str):
    entry = _cache.get(key)
    if entry and (time.time() - entry[0]) < CACHE_TTL:
        return entry[1]
    return None


def _set_cached(key: str, value: object):
    _cache[key] = (time.time(), value)


@router.get("/overview", response_model=OverviewStats)
def get_overview(db: Session = Depends(get_db)):
    cached = _get_cached("overview")
    if cached:
        return cached

    total_plays = db.query(func.count(ListeningHistory.id)).scalar() or 0
    unique_tracks = (
        db.query(func.count(func.distinct(ListeningHistory.track_id))).scalar() or 0
    )
    unique_artists = (
        db.query(func.count(func.distinct(Track.artist_name)))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .scalar()
        or 0
    )
    total_ms = (
        db.query(func.sum(Track.duration_ms))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .scalar()
        or 0
    )
    top_artist_row = (
        db.query(Track.artist_name, func.count().label("cnt"))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .group_by(Track.artist_name)
        .order_by(func.count().desc())
        .first()
    )
    top_track_row = (
        db.query(Track.name, func.count().label("cnt"))
        .join(ListeningHistory, ListeningHistory.track_id == Track.id)
        .group_by(Track.id)
        .order_by(func.count().desc())
        .first()
    )

    result = OverviewStats(
        total_plays=total_plays,
        unique_tracks=unique_tracks,
        unique_artists=unique_artists,
        total_listening_ms=total_ms,
        top_artist=top_artist_row[0] if top_artist_row else None,
        top_track=top_track_row[0] if top_track_row else None,
    )
    _set_cached("overview", result)
    return result


@router.get("/top-tracks", response_model=list[TopItemOut])
def get_top_tracks(
    time_range: str = Query("medium_term"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return (
        db.query(TopItem)
        .filter(TopItem.item_type == "track", TopItem.time_range == time_range)
        .order_by(TopItem.snapshot_date.desc(), TopItem.rank)
        .limit(limit)
        .all()
    )


@router.get("/top-artists", response_model=list[TopItemOut])
def get_top_artists(
    time_range: str = Query("medium_term"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return (
        db.query(TopItem)
        .filter(TopItem.item_type == "artist", TopItem.time_range == time_range)
        .order_by(TopItem.snapshot_date.desc(), TopItem.rank)
        .limit(limit)
        .all()
    )


@router.get("/genres", response_model=list[GenreCount])
def get_genre_distribution(
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db),
):
    cached = _get_cached(f"genres_{limit}")
    if cached:
        return cached

    artists = db.query(Artist.genres).filter(Artist.genres != "[]").all()
    genre_counts: dict[str, int] = {}
    for (genres_json,) in artists:
        try:
            genres = json.loads(genres_json)
        except (json.JSONDecodeError, TypeError):
            continue
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    result = [GenreCount(genre=g, count=c) for g, c in sorted_genres[:limit]]
    _set_cached(f"genres_{limit}", result)
    return result


@router.get("/listening-timeline")
def get_listening_timeline(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timedelta

    cutoff = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            func.date(ListeningHistory.played_at).label("day"),
            func.count().label("plays"),
        )
        .filter(ListeningHistory.played_at >= cutoff)
        .group_by(func.date(ListeningHistory.played_at))
        .order_by(func.date(ListeningHistory.played_at))
        .all()
    )
    return [{"date": row.day, "plays": row.plays} for row in rows]
