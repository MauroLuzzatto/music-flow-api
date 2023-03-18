import logging
import logging.config
import os
from typing import Optional, Tuple

from dotenv import load_dotenv

from music_flow.core.spotify_api import SpotifyAPI
from music_flow.core.utils import path_env

load_dotenv(path_env)
INCLUDE_AUDIO_ANALYSIS = (
    bool(os.getenv("INCLUDE_AUDIO_ANALYSIS_API")) if not os.getenv("API") else False
)


logger = logging.getLogger(__name__)

spotify_api = SpotifyAPI()


def get_song_data_metadata(response: dict) -> dict:
    """get the song data from the spotify api for a given track"""
    try:
        song = response["tracks"]["items"][0]["name"]
        artists_dict = response["tracks"]["items"][0]["artists"]
        artists = [artist["name"] for artist in artists_dict]
        album = response["tracks"]["items"][0]["album"]["name"]
    except (IndexError, KeyError):
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
        "metadata": {},
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

        data["metadata"] = get_song_data_metadata(response)  # type: ignore

    endpoints = [
        (
            "audio_features",
            spotify_api.get_audio_features,
            "Failed to fetched data from Spotify API audio features endpoint.",
        ),
        (
            "track",
            spotify_api.get_track,
            "Failed to fetched data from Sptofiy API track endpoint.",
        ),
    ]

    if INCLUDE_AUDIO_ANALYSIS:
        print("Including audio analysis")
        endpoints.append(
            (
                "audio_analysis",
                spotify_api.get_audio_analysis,
                "Failed to fetched data from Spotify API audio analysis endpoint.",
            )
        )

    for name, function_call, error_description in endpoints:
        response, status_code = function_call(track_id)
        if status_code == 200:
            data[name] = response
        else:
            data["status"] = "failed"
            data["failure_type"] = name
            data["description"] = error_description

            return data, status_code

    data["status"] = "success"
    data["failure_type"] = None  # type: ignore
    data["description"] = "Raw audio features from Spotify API fetched successfully."
    return data, status_code  # type: ignore


if __name__ == "__main__":
    track_name = ""
    artist_name = ""
    data, _ = get_raw_features(track_name, artist_name)
