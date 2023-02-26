import os
from typing import Optional, Tuple

from dotenv import load_dotenv

from music_flow.core.utils import dotenv_path

load_dotenv(dotenv_path)

INCLUDE_AUDIO_ANALYSIS_DATASET = (
    bool(os.getenv("INCLUDE_AUDIO_ANALYSIS_DATASET")) if not os.getenv("API") else False
)


def format_features(
    data: dict,
    track_name: str,
    artist_name: str,
    flattened: Optional[bool] = True,
    hash: Optional[str] = None,
) -> dict:
    """format the features from the spotify api for a given track"""

    features = {}

    try:
        track = data["track"]
        duration_ms = track["duration_ms"]
        explicit = track["explicit"]
        popularity = track["popularity"]
        isrc = track["external_ids"]["isrc"]
        number_of_available_markets = len(track["available_markets"])
        num_artists = len(track["artists"])
    except KeyError as e:
        print(e)
        return {}

    track_dict = {
        "track_name": track_name,
        "artist_name": artist_name,
        "number_of_available_markets": number_of_available_markets,
        "num_artists": num_artists,
        "duration_ms": duration_ms,
        "explicit": explicit,
        "popularity": popularity,
        "isrc": isrc,
    }
    features["track"] = track_dict

    try:
        album = track["album"]["name"]
        release_date = track["album"]["release_date"]
        release_date_precision = track["album"]["release_date_precision"]
        # album_type = track["album"]["album_type"]
    except KeyError as e:
        print(e)
        return {}

    year, month, day, date_is_complete = process_release_date(release_date)

    album_dict = {
        "release_date_precision": release_date_precision,
        "release_date": release_date,
        "release_year": year,
        "release_month": month,
        "release_day": day,
        "date_is_complete": date_is_complete,
        "album": album,
    }

    features["album"] = album_dict

    try:
        audio_features = data["audio_features"]
    except KeyError as e:
        print(e)
        return {}

    features["audio_features"] = audio_features

    if INCLUDE_AUDIO_ANALYSIS_DATASET and "audio_analysis" in data:
        audio_analysis = data["audio_analysis"]
        features["audio_analysis"] = audio_analysis

    if flattened:
        features_flattend = {}
        for _, sub_value in features.items():
            for key, value in sub_value.items():
                features_flattend[key] = value
        features = features_flattend

    return features


def process_release_date(release_date: str) -> Tuple[int, int, int, bool]:
    """_summary_

    Args:
        release_date (str): _description_

    Returns:
        Tuple[int, int, int, bool]: _description_
    """
    split_date = release_date.split("-")
    day = 1
    month = 1
    if len(split_date) == 3:
        year, month, day = split_date
        date_is_complete = True
    elif len(split_date) == 2:
        year, month = split_date
        date_is_complete = False
    else:
        year = split_date[0]
        date_is_complete = False
    return int(year), int(month), int(day), date_is_complete
