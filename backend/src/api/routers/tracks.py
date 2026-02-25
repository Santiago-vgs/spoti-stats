from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import TrackOut
from src.db.models import Track

router = APIRouter(tags=["tracks"])


@router.get("/tracks", response_model=list[TrackOut])
def get_tracks(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Track)
    if search:
        query = query.filter(
            Track.name.ilike(f"%{search}%") | Track.artist_name.ilike(f"%{search}%")
        )
    return query.order_by(Track.name).offset(offset).limit(limit).all()
