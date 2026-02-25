from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.db.models import AudioFeature, DailyListeningSummary, HourlyActivity, Insight

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("")
def get_insights(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Insight)
        .order_by(Insight.generated_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "content": r.content,
            "insight_type": r.insight_type,
            "generated_at": r.generated_at.isoformat() if r.generated_at else None,
        }
        for r in rows
    ]


@router.get("/mood-profile")
def get_mood_profile(db: Session = Depends(get_db)):
    """Return cluster profiles with average features per cluster."""
    from sqlalchemy import func

    clusters = (
        db.query(
            AudioFeature.cluster_id,
            func.count().label("count"),
            func.avg(AudioFeature.danceability).label("danceability"),
            func.avg(AudioFeature.energy).label("energy"),
            func.avg(AudioFeature.valence).label("valence"),
            func.avg(AudioFeature.acousticness).label("acousticness"),
            func.avg(AudioFeature.instrumentalness).label("instrumentalness"),
            func.avg(AudioFeature.speechiness).label("speechiness"),
            func.avg(AudioFeature.liveness).label("liveness"),
        )
        .filter(AudioFeature.cluster_id.isnot(None))
        .group_by(AudioFeature.cluster_id)
        .all()
    )

    return [
        {
            "cluster_id": c.cluster_id,
            "count": c.count,
            "features": {
                "danceability": round(c.danceability, 3),
                "energy": round(c.energy, 3),
                "valence": round(c.valence, 3),
                "acousticness": round(c.acousticness, 3),
                "instrumentalness": round(c.instrumentalness, 3),
                "speechiness": round(c.speechiness, 3),
                "liveness": round(c.liveness, 3),
            },
        }
        for c in clusters
    ]


@router.get("/heatmap")
def get_heatmap(db: Session = Depends(get_db)):
    rows = db.query(HourlyActivity).all()
    return [
        {
            "day_of_week": r.day_of_week,
            "hour": r.hour,
            "play_count": r.play_count,
        }
        for r in rows
    ]


@router.get("/daily-summary")
def get_daily_summary(
    limit: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(DailyListeningSummary)
        .order_by(DailyListeningSummary.date.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "date": r.date,
            "total_plays": r.total_plays,
            "total_duration_ms": r.total_duration_ms,
            "unique_tracks": r.unique_tracks,
            "unique_artists": r.unique_artists,
            "avg_energy": r.avg_energy,
            "avg_valence": r.avg_valence,
            "avg_danceability": r.avg_danceability,
        }
        for r in rows
    ]
