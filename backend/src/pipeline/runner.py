import argparse
from datetime import datetime

from sqlalchemy import func

from src.db.database import SessionLocal
from src.db.init_db import create_tables
from src.db.models import AudioFeature, ListeningHistory, PipelineRun, Track
from src.pipeline.ingest import (
    ingest_audio_features,
    ingest_playlists,
    ingest_recently_played,
    ingest_top_artists,
    ingest_top_tracks,
)
from src.pipeline.load import (
    load_artists,
    load_audio_features,
    load_listening_history,
    load_playlists,
    load_top_items,
    rebuild_daily_summaries,
    rebuild_hourly_activity,
)
from src.pipeline.transform import (
    transform_artist,
    transform_audio_features,
    transform_playlist,
    transform_playlist_tracks,
    transform_recently_played,
    transform_top_items,
)
from src.spotify.client import SpotifyWrapper


def _get_high_water_mark(session) -> int | None:
    """Get the last played_at timestamp (ms since epoch) from previous runs."""
    last_run = (
        session.query(PipelineRun)
        .filter(PipelineRun.status == "ok")
        .order_by(PipelineRun.finished_at.desc())
        .first()
    )
    if last_run and last_run.last_played_at:
        return int(last_run.last_played_at.timestamp() * 1000)
    return None


def _get_tracks_missing_features(session) -> list[str]:
    """Find track IDs that are in the tracks table but not in audio_features."""
    existing = session.query(AudioFeature.track_id).subquery()
    missing = (
        session.query(Track.id)
        .outerjoin(existing, Track.id == existing.c.track_id)
        .filter(existing.c.track_id.is_(None))
        .all()
    )
    return [r[0] for r in missing]


def run_pipeline(
    recent: bool = True,
    top: bool = True,
    playlists: bool = False,
):
    create_tables()
    wrapper = SpotifyWrapper()
    session = SessionLocal()

    # Record pipeline run
    run = PipelineRun(started_at=datetime.utcnow(), status="running")
    session.add(run)
    session.commit()

    rows_ingested = 0

    try:
        # --- Step 1: Recently played (with high-water mark) ---
        if recent:
            after_ms = _get_high_water_mark(session)
            print(f"Ingesting recently played (after={after_ms})...")
            raw = ingest_recently_played(wrapper, after_ms=after_ms)
            transformed = transform_recently_played(raw)
            load_listening_history(session, transformed)
            rows_ingested += len(transformed)
            print(f"  Loaded {len(transformed)} history records.")

            # Track the latest played_at for next run
            if transformed:
                latest = max(item["played_at"] for item in transformed)
                run.last_played_at = latest

        # --- Step 2: Top tracks ---
        if top:
            print("Ingesting top tracks...")
            top_tracks_raw = ingest_top_tracks(wrapper)
            for time_range, items in top_tracks_raw.items():
                transformed = transform_top_items(items, "track", time_range)
                load_top_items(session, transformed)
                rows_ingested += len(transformed)
                print(f"  Top tracks ({time_range}): {len(transformed)} items.")

            print("Ingesting top artists...")
            top_artists_raw = ingest_top_artists(wrapper)
            for time_range, items in top_artists_raw.items():
                load_artists(session, items, transform_artist)
                transformed = transform_top_items(items, "artist", time_range)
                load_top_items(session, transformed)
                rows_ingested += len(transformed)
                print(f"  Top artists ({time_range}): {len(transformed)} items.")

        # --- Step 3: Playlists ---
        if playlists:
            print("Ingesting playlists...")
            raw_playlists = ingest_playlists(wrapper)
            pl_data_list = []
            pl_tracks = {}
            for raw in raw_playlists:
                tracks_raw = raw.pop("_tracks", [])
                pl_data = transform_playlist(raw)
                pl_data_list.append(pl_data)
                pl_tracks[pl_data["id"]] = transform_playlist_tracks(
                    tracks_raw, pl_data["id"]
                )
            load_playlists(session, pl_data_list, pl_tracks)
            rows_ingested += len(pl_data_list)
            print(f"  Loaded {len(pl_data_list)} playlists.")

        # --- Step 4: Audio features (for tracks missing them) ---
        print("Fetching audio features...")
        missing_ids = _get_tracks_missing_features(session)
        has_audio_features = session.query(AudioFeature).count() > 0
        if missing_ids:
            try:
                raw_features = ingest_audio_features(wrapper, missing_ids)
                if raw_features:
                    transformed_features = transform_audio_features(raw_features)
                    load_audio_features(session, transformed_features)
                    rows_ingested += len(transformed_features)
                    has_audio_features = True
                    print(f"  Loaded audio features for {len(transformed_features)} tracks.")
                else:
                    print("  Audio features API unavailable (deprecated by Spotify). Skipping.")
            except Exception as e:
                print(f"  Audio features failed: {e}. Skipping.")
        else:
            has_audio_features = session.query(AudioFeature).count() > 0
            print("  All tracks already have audio features.")

        # --- Step 5: Mood clustering ---
        if has_audio_features:
            print("Running mood clustering...")
            try:
                from src.pipeline.clustering import run_clustering
                run_clustering(session)
            except Exception as e:
                print(f"  Clustering skipped: {e}")
        else:
            print("Skipping mood clustering (no audio features available).")

        # --- Step 6: Rebuild aggregates ---
        print("Rebuilding daily summaries...")
        rebuild_daily_summaries(session)
        print("Rebuilding hourly activity heatmap...")
        rebuild_hourly_activity(session)

        # --- Step 7: Generate insights ---
        print("Generating insights...")
        try:
            from src.pipeline.insights import generate_insights
            generate_insights(session)
        except Exception as e:
            print(f"  Insight generation skipped: {e}")

        # Mark run as successful
        run.status = "ok"
        run.finished_at = datetime.utcnow()
        run.rows_ingested = rows_ingested
        session.commit()
        print(f"Pipeline complete. {rows_ingested} rows ingested.")

    except Exception:
        session.rollback()
        # Record failure
        run.status = "error"
        run.finished_at = datetime.utcnow()
        import traceback
        run.error_message = traceback.format_exc()
        session.add(run)
        session.commit()
        raise
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Spotify Stats ETL Pipeline")
    parser.add_argument("--no-recent", action="store_true", help="Skip recently played")
    parser.add_argument("--no-top", action="store_true", help="Skip top tracks/artists")
    parser.add_argument("--playlists", action="store_true", help="Include playlists")
    parser.add_argument("--all", action="store_true", help="Run all pipelines")
    args = parser.parse_args()

    run_pipeline(
        recent=not args.no_recent or args.all,
        top=not args.no_top or args.all,
        playlists=args.playlists or args.all,
    )


if __name__ == "__main__":
    main()
