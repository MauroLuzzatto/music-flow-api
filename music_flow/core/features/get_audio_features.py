import logging
import logging.config
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from music_flow.config.core import settings
from music_flow.core.spotify_api import SpotifyAPI

logger = logging.getLogger(__name__)

spotify_api = SpotifyAPI()
# TODO: allow for batch downloading of api requests

@dataclass
class Endpoint:
    """Class for defintion the API endpoints that called."""

    name: str
    func: Callable
    descripton: str


def get_song_data_metadata(response: dict) -> dict:
    """get the song data from the spotify api for a given track"""
    try:
        song = response["name"]
        album = response["album"]["name"]
        artists_dict = response["album"]["artists"]
        artists = [artist["name"] for artist in artists_dict]
    except (IndexError, KeyError) as e:
        print(f"Error: could not get the metadata - {e}")
        return {}
    metadata = {"song": song, "artist": artists, "album": album}
    return metadata


def get_raw_features(
    track_name: str, artist_name: str, track_id: Optional[str] = None
) -> Tuple[dict, int]:
    """get the features from the Spotify API for a given track"""

    data = {
        "track_name": track_name,
        "artist_name": artist_name,
    }

    if not track_id:
        url = spotify_api.search_track_url(track_name, artist_name)
        response, status_code = spotify_api.get_request(url)
        logger.info(f"status_code: {status_code}")
        try:
            track_id = response["tracks"]["items"][0]["id"]
            failed = False
        except (IndexError, KeyError):
            failed = True

        if status_code != 200 or failed:
            data["status"] = "failed"
            data["failure_type"] = "search_track_url"
            data["description"] = "Failed to fetched track_id from Spotfiy API."
            return data, status_code

    endpoints = [
        Endpoint(
            name="audio_features",
            func=spotify_api.get_audio_features,
            descripton=(
                "Failed to fetched data from Spotify API audio features endpoint."
            ),
        ),
        Endpoint(
            name="track",
            func=spotify_api.get_track,
            descripton="Failed to fetched data from Sptofiy API track endpoint.",
        ),
    ]

    if settings.INCLUDE_AUDIO_ANALYSIS_API:
        logger.info("Including audio analysis")
        endpoints.append(
            Endpoint(
                name="audio_analysis",
                func=spotify_api.get_audio_analysis,
                descripton=(
                    "Failed to fetched data from Spotify API audio analysis endpoint."
                ),
            ),
        )
    for endpoint in endpoints:
        name = endpoint.name
        response, status_code = endpoint.func(track_id)
        logger.info(f"endpoint: {endpoint.name} - status_code: {status_code}")
        if status_code == 200:
            data[name] = response
        else:
            data["status"] = "failed"
            data["failure_type"] = name
            data["description"] = endpoint.descripton
            return data, status_code

    data["status"] = "success"
    data["failure_type"] = None  # type: ignore
    data["description"] = "Raw audio features from Spotify API fetched successfully."
    data["metadata"] = get_song_data_metadata(data["track"])  # type: ignore
    return data, status_code  # type: ignore


if __name__ == "__main__":
    track_name = ""
    artist_name = ""
    data, _ = get_raw_features(track_name, artist_name)
