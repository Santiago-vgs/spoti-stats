from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import ArtistOut
from src.db.models import Artist

router = APIRouter(tags=["artists"])


@router.get("/artists", response_model=list[ArtistOut])
def get_artists(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Artist).order_by(Artist.name).offset(offset).limit(limit).all()
