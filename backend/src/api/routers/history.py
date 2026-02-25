from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from src.api.deps import get_db
from src.api.schemas import HistoryOut
from src.db.models import ListeningHistory

router = APIRouter(tags=["history"])


@router.get("/history", response_model=list[HistoryOut])
def get_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    date_from: str | None = None,
    date_to: str | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(ListeningHistory)
        .options(joinedload(ListeningHistory.track))
        .order_by(ListeningHistory.played_at.desc())
    )
    if date_from:
        query = query.filter(ListeningHistory.played_at >= date_from)
    if date_to:
        query = query.filter(ListeningHistory.played_at <= date_to)
    return query.offset(offset).limit(limit).all()
