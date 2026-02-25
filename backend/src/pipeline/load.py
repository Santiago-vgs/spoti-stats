from datetime import datetime

from sqlalchemy import Integer, func
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.orm import Session

from src.db.models import (
    Artist,
    AudioFeature,
    DailyListeningSummary,
    HourlyActivity,
    ListeningHistory,
    Playlist,
    PlaylistTrack,
    TopItem,
    Track,
    track_artists,
)


def _bulk_upsert_tracks(session: Session, tracks: list[dict]):
    if not tracks:
        return
    stmt = sqlite_insert(Track.__table__).values(tracks)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "name": stmt.excluded.name,
            "artist_name": stmt.excluded.artist_name,
            "album_name": stmt.excluded.album_name,
            "album_image_url": stmt.excluded.album_image_url,
            "duration_ms": stmt.excluded.duration_ms,
            "popularity": stmt.excluded.popularity,
            "spotify_url": stmt.excluded.spotify_url,
            "preview_url": stmt.excluded.preview_url,
            "updated_at": datetime.utcnow(),
        },
    )
    session.execute(stmt)


def _bulk_upsert_artists(session: Session, artists: list[dict]):
    if not artists:
        return
    stmt = sqlite_insert(Artist.__table__).values(artists)
    stmt = stmt.on_conflict_do_update(
        index_elements=["id"],
        set_={
            "name": stmt.excluded.name,
            "genres": stmt.excluded.genres,
            "popularity": stmt.excluded.popularity,
            "image_url": stmt.excluded.image_url,
            "spotify_url": stmt.excluded.spotify_url,
            "updated_at": datetime.utcnow(),
        },
    )
    session.execute(stmt)


def _bulk_link_track_artists(session: Session, links: list[dict]):
    if not links:
        return
    stmt = sqlite_insert(track_artists).values(links)
    stmt = stmt.on_conflict_do_nothing()
    session.execute(stmt)


def load_listening_history(session: Session, items: list[dict]):
    track_rows = []
    artist_stubs = []
    artist_links = []
    history_rows = []

    for item in items:
        track_data = dict(item["track"])
        artist_ids = track_data.pop("_artist_ids", [])
        artists_raw = track_data.pop("_artists_raw", [])
        track_rows.append(track_data)

        for raw_artist in artists_raw:
            artist_stubs.append({
                "id": raw_artist["id"],
                "name": raw_artist["name"],
                "genres": "[]",
                "popularity": None,
                "image_url": None,
                "spotify_url": raw_artist.get("external_urls", {}).get("spotify"),
            })

        for aid in artist_ids:
            artist_links.append({"track_id": track_data["id"], "artist_id": aid})

        history_rows.append({
            "track_id": track_data["id"],
            "played_at": item["played_at"],
            "context_type": item.get("context_type"),
        })

    _bulk_upsert_tracks(session, track_rows)
    # Only insert artist stubs if they don't already exist (don't overwrite full artist data)
    if artist_stubs:
        stmt = sqlite_insert(Artist.__table__).values(artist_stubs)
        stmt = stmt.on_conflict_do_nothing()
        session.execute(stmt)
    _bulk_link_track_artists(session, artist_links)

    if history_rows:
        stmt = sqlite_insert(ListeningHistory.__table__).values(history_rows)
        stmt = stmt.on_conflict_do_nothing()
        session.execute(stmt)

    session.commit()


def load_top_items(session: Session, items: list[dict]):
    if not items:
        return
    stmt = sqlite_insert(TopItem.__table__).values(items)
    stmt = stmt.on_conflict_do_update(
        index_elements=["item_type", "item_id", "time_range", "snapshot_date"],
        set_={
            "rank": stmt.excluded.rank,
            "item_name": stmt.excluded.item_name,
            "image_url": stmt.excluded.image_url,
            "extra_data": stmt.excluded.extra_data,
        },
    )
    session.execute(stmt)
    session.commit()


def load_artists(session: Session, artists_raw: list[dict], transform_fn):
    rows = [transform_fn(raw) for raw in artists_raw]
    _bulk_upsert_artists(session, rows)
    session.commit()


def load_playlists(session: Session, playlists: list[dict], playlist_tracks: dict[str, list[dict]]):
    if playlists:
        stmt = sqlite_insert(Playlist.__table__).values(playlists)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": stmt.excluded.name,
                "description": stmt.excluded.description,
                "owner_name": stmt.excluded.owner_name,
                "image_url": stmt.excluded.image_url,
                "total_tracks": stmt.excluded.total_tracks,
                "spotify_url": stmt.excluded.spotify_url,
                "snapshot_id": stmt.excluded.snapshot_id,
                "updated_at": datetime.utcnow(),
            },
        )
        session.execute(stmt)

    for pl_id, items in playlist_tracks.items():
        # Collect track data first
        track_rows = []
        pt_rows = []
        for item in items:
            item = dict(item)
            track_raw = item.pop("_track_raw", None)
            if track_raw:
                from src.pipeline.transform import transform_track
                track_data = transform_track(track_raw)
                track_data.pop("_artist_ids", None)
                track_data.pop("_artists_raw", None)
                track_rows.append(track_data)
            pt_rows.append(item)

        _bulk_upsert_tracks(session, track_rows)

        # Clear and re-insert playlist tracks
        session.query(PlaylistTrack).filter_by(playlist_id=pl_id).delete()
        if pt_rows:
            session.execute(PlaylistTrack.__table__.insert().values(pt_rows))

    session.commit()


def load_audio_features(session: Session, features: list[dict]):
    if not features:
        return
    stmt = sqlite_insert(AudioFeature.__table__).values(features)
    stmt = stmt.on_conflict_do_update(
        index_elements=["track_id"],
        set_={
            "danceability": stmt.excluded.danceability,
            "energy": stmt.excluded.energy,
            "valence": stmt.excluded.valence,
            "tempo": stmt.excluded.tempo,
            "acousticness": stmt.excluded.acousticness,
            "instrumentalness": stmt.excluded.instrumentalness,
            "speechiness": stmt.excluded.speechiness,
            "liveness": stmt.excluded.liveness,
            "loudness": stmt.excluded.loudness,
            "key": stmt.excluded.key,
            "mode": stmt.excluded.mode,
            "time_signature": stmt.excluded.time_signature,
        },
    )
    session.execute(stmt)
    session.commit()


def update_cluster_assignments(session: Session, assignments: dict[str, int]):
    """Update cluster_id on AudioFeature rows."""
    for track_id, cluster_id in assignments.items():
        session.query(AudioFeature).filter_by(track_id=track_id).update(
            {"cluster_id": cluster_id}
        )
    session.commit()


def rebuild_daily_summaries(session: Session):
    """Rebuild the daily_listening_summary table from listening_history."""
    session.query(DailyListeningSummary).delete()

    rows = (
        session.query(
            func.date(ListeningHistory.played_at).label("date"),
            func.count().label("total_plays"),
            func.sum(Track.duration_ms).label("total_duration_ms"),
            func.count(func.distinct(ListeningHistory.track_id)).label("unique_tracks"),
            func.count(func.distinct(Track.artist_name)).label("unique_artists"),
        )
        .join(Track, ListeningHistory.track_id == Track.id)
        .group_by(func.date(ListeningHistory.played_at))
        .all()
    )

    audio_rows = (
        session.query(
            func.date(ListeningHistory.played_at).label("date"),
            func.avg(AudioFeature.energy).label("avg_energy"),
            func.avg(AudioFeature.valence).label("avg_valence"),
            func.avg(AudioFeature.danceability).label("avg_danceability"),
        )
        .join(Track, ListeningHistory.track_id == Track.id)
        .join(AudioFeature, AudioFeature.track_id == Track.id, isouter=True)
        .group_by(func.date(ListeningHistory.played_at))
        .all()
    )
    audio_map = {r.date: r for r in audio_rows}

    summaries = []
    for row in rows:
        audio = audio_map.get(row.date)
        summaries.append({
            "date": row.date,
            "total_plays": row.total_plays,
            "total_duration_ms": row.total_duration_ms or 0,
            "unique_tracks": row.unique_tracks,
            "unique_artists": row.unique_artists,
            "avg_energy": audio.avg_energy if audio else None,
            "avg_valence": audio.avg_valence if audio else None,
            "avg_danceability": audio.avg_danceability if audio else None,
        })

    if summaries:
        session.execute(DailyListeningSummary.__table__.insert().values(summaries))
    session.commit()


def rebuild_hourly_activity(session: Session):
    """Rebuild the hourly_activity heatmap table."""
    session.query(HourlyActivity).delete()

    rows = (
        session.query(
            func.cast(func.strftime("%w", ListeningHistory.played_at), Integer).label("dow"),
            func.cast(func.strftime("%H", ListeningHistory.played_at), Integer).label("hour"),
            func.count().label("cnt"),
        )
        .group_by("dow", "hour")
        .all()
    )

    if rows:
        activity = []
        for row in rows:
            # SQLite %w: 0=Sunday. Convert to 0=Monday.
            dow = (row.dow - 1) % 7
            activity.append({"day_of_week": dow, "hour": row.hour, "play_count": row.cnt})
        stmt = sqlite_insert(HourlyActivity.__table__).values(activity)
        stmt = stmt.on_conflict_do_update(
            index_elements=["day_of_week", "hour"],
            set_={"play_count": stmt.excluded.play_count},
        )
        session.execute(stmt)
    session.commit()
