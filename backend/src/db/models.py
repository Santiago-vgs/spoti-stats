from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.db.database import Base

track_artists = Table(
    "track_artists",
    Base.metadata,
    Column("track_id", String, ForeignKey("tracks.id"), primary_key=True),
    Column("artist_id", String, ForeignKey("artists.id"), primary_key=True),
)


class Artist(Base):
    __tablename__ = "artists"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    genres = Column(Text, default="[]")  # JSON array as text
    popularity = Column(Integer)
    image_url = Column(String)
    spotify_url = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tracks = relationship("Track", secondary=track_artists, back_populates="artists")


class Track(Base):
    __tablename__ = "tracks"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    artist_name = Column(String)  # denormalized for easy queries
    album_name = Column(String)
    album_image_url = Column(String)
    duration_ms = Column(Integer)
    popularity = Column(Integer)
    spotify_url = Column(String)
    preview_url = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    artists = relationship("Artist", secondary=track_artists, back_populates="tracks")
    history = relationship("ListeningHistory", back_populates="track")


class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    track_id = Column(String, ForeignKey("tracks.id"), nullable=False)
    played_at = Column(DateTime, nullable=False)
    context_type = Column(String)  # album, playlist, artist, etc.

    track = relationship("Track", back_populates="history")

    __table_args__ = (
        UniqueConstraint("track_id", "played_at", name="uq_track_played_at"),
        Index("ix_history_played_at", "played_at"),
        Index("ix_history_track_id", "track_id"),
    )


class TopItem(Base):
    __tablename__ = "top_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String, nullable=False)  # "track" or "artist"
    item_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    time_range = Column(String, nullable=False)  # short_term, medium_term, long_term
    rank = Column(Integer, nullable=False)
    snapshot_date = Column(String, nullable=False)  # YYYY-MM-DD
    image_url = Column(String)
    extra_data = Column(Text, default="{}")  # JSON for flexible metadata

    __table_args__ = (
        UniqueConstraint(
            "item_type", "item_id", "time_range", "snapshot_date",
            name="uq_top_item_snapshot",
        ),
        Index("ix_top_item_query", "item_type", "time_range", "snapshot_date", "rank"),
    )


class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    owner_name = Column(String)
    image_url = Column(String)
    total_tracks = Column(Integer)
    spotify_url = Column(String)
    snapshot_id = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    playlist_tracks = relationship("PlaylistTrack", back_populates="playlist")


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(String, ForeignKey("playlists.id"), nullable=False)
    track_id = Column(String, ForeignKey("tracks.id"), nullable=False)
    added_at = Column(DateTime)
    position = Column(Integer)

    playlist = relationship("Playlist", back_populates="playlist_tracks")
    track = relationship("Track")

    __table_args__ = (
        UniqueConstraint("playlist_id", "track_id", name="uq_playlist_track"),
        Index("ix_playlist_track_playlist", "playlist_id", "position"),
    )


class AudioFeature(Base):
    __tablename__ = "audio_features"

    track_id = Column(String, ForeignKey("tracks.id"), primary_key=True)
    danceability = Column(Float)
    energy = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    speechiness = Column(Float)
    liveness = Column(Float)
    loudness = Column(Float)
    key = Column(Integer)
    mode = Column(Integer)
    time_signature = Column(Integer)
    cluster_id = Column(Integer)  # mood cluster assignment


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime)
    status = Column(String, nullable=False, default="running")  # running, ok, error
    error_message = Column(Text)
    rows_ingested = Column(Integer, default=0)
    last_played_at = Column(DateTime)  # high-water mark cursor


class DailyListeningSummary(Base):
    __tablename__ = "daily_listening_summary"

    date = Column(String, primary_key=True)  # YYYY-MM-DD
    total_plays = Column(Integer, default=0)
    total_duration_ms = Column(Integer, default=0)
    unique_tracks = Column(Integer, default=0)
    unique_artists = Column(Integer, default=0)
    avg_energy = Column(Float)
    avg_valence = Column(Float)
    avg_danceability = Column(Float)


class HourlyActivity(Base):
    __tablename__ = "hourly_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    hour = Column(Integer, nullable=False)  # 0-23
    play_count = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("day_of_week", "hour", name="uq_hourly_activity"),
    )


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    generated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    insight_type = Column(String, nullable=False)  # weekly, anomaly, milestone
    content = Column(Text, nullable=False)
    metadata_json = Column(Text, default="{}")  # extra context
