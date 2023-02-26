from __future__ import annotations

from pydantic import BaseModel


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
    release_date: str
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
    type: str
    id: str
    uri: str
    track_href: str
    analysis_url: str
    duration_ms: int
    time_signature: int


class Features(BaseModel):
    track: Track
    album: Album
    audio_features: AudioFeatures
