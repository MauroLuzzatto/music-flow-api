from __future__ import annotations

from pydantic import BaseModel
from app.schemas.raw_features import Metadata

class Track(BaseModel):
    track_name: str
    artist_name: str
    number_of_available_markets: int
    num_artists: int
    duration_ms: int
    explicit: bool
    popularity: int
    isrc: str


class Album(BaseModel):
    release_date_precision: str
    release_year: int
    release_month: int
    release_day: int
    date_is_complete: bool
    album: str


class AudioFeatures(BaseModel):
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    id: str
    time_signature: int


class Features(BaseModel):
    track: Track
    album: Album
    audio_features: AudioFeatures
    metadata:Metadata
