from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from src.api.deps import get_db
from src.api.schemas import PlaylistOut, PlaylistTrackOut
from src.db.models import Playlist, PlaylistTrack

router = APIRouter(tags=["playlists"])


@router.get("/playlists", response_model=list[PlaylistOut])
def get_playlists(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return db.query(Playlist).order_by(Playlist.name).offset(offset).limit(limit).all()


@router.get("/playlists/{playlist_id}", response_model=PlaylistOut)
def get_playlist(playlist_id: str, db: Session = Depends(get_db)):
    pl = db.get(Playlist, playlist_id)
    if not pl:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return pl


@router.get("/playlists/{playlist_id}/tracks", response_model=list[PlaylistTrackOut])
def get_playlist_tracks(playlist_id: str, db: Session = Depends(get_db)):
    return (
        db.query(PlaylistTrack)
        .options(joinedload(PlaylistTrack.track))
        .filter(PlaylistTrack.playlist_id == playlist_id)
        .order_by(PlaylistTrack.position)
        .all()
    )
