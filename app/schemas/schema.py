from typing import Any, List, Union

from pydantic import BaseModel


class Health(BaseModel):
    name: str
    description: str
    api_version: str
    model_version: str
    project_url: str


class SongMetadataModel(BaseModel):
    song: str
    artist: List[str]
    album: str


class Message(BaseModel):
    emoji: str
    text: str


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


class Prediction(BaseModel):
    song: str
    artist: str
    prediction: float
    description: str
    song_metadata: SongMetadataModel
    message: Message
    preview_url: Union[str, None]


class Metadata(BaseModel):
    song: str
    artist: List[str]
    album: str


class ExternalUrls(BaseModel):
    spotify: str


class Artist(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class ExternalUrls1(BaseModel):
    spotify: str


class Image(BaseModel):
    height: int
    url: str
    width: int


class Album(BaseModel):
    album_type: str
    artists: List[Artist]
    available_markets: List[str]
    external_urls: ExternalUrls1
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str


class ExternalUrls2(BaseModel):
    spotify: str


class Artist1(BaseModel):
    external_urls: ExternalUrls2
    href: str
    id: str
    name: str
    type: str
    uri: str


class ExternalIds(BaseModel):
    isrc: str


class ExternalUrls3(BaseModel):
    spotify: str


class Track(BaseModel):
    album: Album
    artists: List[Artist1]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalIds
    external_urls: ExternalUrls3
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: Any
    track_number: int
    type: str
    uri: str


class RawFeatures(BaseModel):
    track_name: str
    artist_name: str
    metadata: Metadata
    audio_features: AudioFeatures
    track: Track
    status: str
    failure_type: Any
