from datetime import datetime

from pydantic import BaseModel


class ArtistOut(BaseModel):
    id: str
    name: str
    genres: str  # JSON string
    popularity: int | None
    image_url: str | None
    spotify_url: str | None

    model_config = {"from_attributes": True}


class TrackOut(BaseModel):
    id: str
    name: str
    artist_name: str | None
    album_name: str | None
    album_image_url: str | None
    duration_ms: int | None
    popularity: int | None
    spotify_url: str | None

    model_config = {"from_attributes": True}


class HistoryOut(BaseModel):
    id: int
    track_id: str
    played_at: datetime
    context_type: str | None
    track: TrackOut | None

    model_config = {"from_attributes": True}


class TopItemOut(BaseModel):
    id: int
    item_type: str
    item_id: str
    item_name: str
    time_range: str
    rank: int
    snapshot_date: str
    image_url: str | None
    extra_data: str  # JSON string

    model_config = {"from_attributes": True}


class PlaylistOut(BaseModel):
    id: str
    name: str
    description: str | None
    owner_name: str | None
    image_url: str | None
    total_tracks: int | None
    spotify_url: str | None

    model_config = {"from_attributes": True}


class PlaylistTrackOut(BaseModel):
    track_id: str
    added_at: datetime | None
    position: int | None
    track: TrackOut | None

    model_config = {"from_attributes": True}


class OverviewStats(BaseModel):
    total_plays: int
    unique_tracks: int
    unique_artists: int
    total_listening_ms: int
    top_artist: str | None
    top_track: str | None


class GenreCount(BaseModel):
    genre: str
    count: int
