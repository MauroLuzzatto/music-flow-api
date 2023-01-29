import json
import os
import time
from pprint import pprint
from typing import Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

from track_recommender.file_handling import load_json
from track_recommender.utils import (
    dotenv_path,
    path_data,
    path_data_lake,
    path_features,
)

load_dotenv(dotenv_path)

INCLUDE_AUDIO_ANALYSIS_DATASET = os.getenv("INCLUDE_AUDIO_ANALYSIS_DATASET")
print(INCLUDE_AUDIO_ANALYSIS_DATASET)


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


def format_features(
    data: dict, track_name: str, artist_name: str, hash: Optional[str] = None
) -> dict:
    """format features from spotify api"""

    empty_dict = {}
    features = {}

    try:
        track = data["track"]
        audio_features = data["audio_features"]
    except KeyError as e:
        print(e)
        return empty_dict

    try:
        duration_ms = track["duration_ms"]
        explicit = track["explicit"]
        popularity = track["popularity"]
        type = track["type"]
        isrc = track["external_ids"]["isrc"]
        album = track["album"]["name"]
        release_date = track["album"]["release_date"]
        album_type = track["album"]["album_type"]
        number_of_available_markets = len(track["available_markets"])
        release_date_precision = track["album"]["release_date_precision"]
        num_artists = len(track["artists"])
    except KeyError as e:
        print(e)
        return empty_dict

    year, month, day, date_is_complete = process_release_date(release_date)

    track_dict = {
        "track_name": track_name,
        "artist_name": artist_name,
        "id_hash": hash,
        "album": album,
        # "album_type": album_type,
        "number_of_available_markets": number_of_available_markets,
        "release_date_precision": release_date_precision,
        "release_date": release_date,
        "release_year": year,
        "release_month": month,
        "release_day": day,
        "date_is_complete": date_is_complete,
        "num_artists": num_artists,
        "duration_ms": duration_ms,
        "explicit": explicit,
        "popularity": popularity,
        "isrc": isrc,
    }

    features.update(track_dict)
    features.update(audio_features)
    # if INCLUDE_AUDIO_ANALYSIS_DATASET:
    #      audio_analysis = data["audio_analysis"]
    #     features.update(audio_analysis)
    return features


def create_audio_features_dataset():
    """_summary_"""

    df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    path_audio_features = os.path.join(path_features, r"audio_features.csv")

    files_set = set(os.listdir(path_data_lake))
    count_failing_tracks = 0
    count_missing_tracks = 0

    dataset = []
    start = time.time()
    for index, row in df.iterrows():

        if int(index) % 800 == 0:  # type: ignore
            time_passed = time.time() - start
            print(f"{index}/{len(df)} - {time_passed/60.:.1f} min")
            print(
                f"missing tracks: {count_missing_tracks} - failing tracks: {count_failing_tracks}"
            )

        track_name = row["track_name"]
        artist_name = row["artist_name"]
        hash = row["hash"]
        filename = f"{hash}.json"

        if filename not in files_set:
            count_missing_tracks += 1
            continue

        path_file = os.path.join(path_data_lake, filename)
        data = load_json(path_file)

        if (
            data["status"] == "failed"
            and not data["failure_reason"] == "audio_analysis"
        ):
            count_failing_tracks += 1
            os.remove(path_file)
            continue

        features = format_features(data, track_name, artist_name, hash)

        if not features:
            count_failing_tracks += 1
            pprint(data["track_name"])
            os.remove(path_file)
            continue

        dataset.append(features)

    df_audio_features = pd.DataFrame(dataset)
    df_audio_features.to_csv(path_audio_features, sep=";")
    print(f"saved: {path_audio_features}")


if __name__ == "__main__":
    create_audio_features_dataset()
