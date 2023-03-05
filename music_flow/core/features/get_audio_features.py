import json
import os
import time
from typing import Optional, Tuple

import pandas as pd
from dotenv import load_dotenv

from music_flow.core.spotify_api import SpotifyAPI
from music_flow.core.utils import path_data, path_data_lake, path_env

load_dotenv(path_env)
INCLUDE_AUDIO_ANALYSIS = (
    bool(os.getenv("INCLUDE_AUDIO_ANALYSIS_API")) if not os.getenv("API") else False
)


spotify_api = SpotifyAPI()


def save_data(data, path, filename):
    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_song_data_metadata(response: dict) -> dict:
    """get the song data from the spotify api for a given track"""
    try:
        song = response["tracks"]["items"][0]["name"]
        artists = [
            artist["name"] for artist in response["tracks"]["items"][0]["artists"]
        ]
        album = response["tracks"]["items"][0]["album"]["name"]
    except (IndexError, KeyError):
        return {}

    metadata = {"song": song, "artist": artists, "album": album}
    return metadata


def get_features(
    track_name: str,
    artist_name: str,
    track_id: Optional[str] = None,
) -> Tuple[dict, int]:
    """get the features from the sptofy api for a given track"""

    data = {
        "track_name": track_name,
        "artist_name": artist_name,
        "metadata": {},
    }

    if not track_id:
        url = spotify_api.search_track_url(track_name, artist_name)
        response, status_code = spotify_api.get_request(url)

        try:
            track_id = response["tracks"]["items"][0]["id"]
            failed = False
        except (IndexError, KeyError):
            failed = True

        if status_code != 200 or failed:
            data["status"] = "failed"
            data["failure_type"] = "search_track_url"
            return data, status_code

        data["metadata"] = get_song_data_metadata(response)  # type: ignore

    endpoints = [
        ("audio_features", spotify_api.get_audio_features),
        ("track", spotify_api.get_track),
    ]

    if INCLUDE_AUDIO_ANALYSIS:
        print("Including audio analysis")
        endpoints.append(("audio_analysis", spotify_api.get_audio_analysis))

    for name, function_call in endpoints:
        response, status_code = function_call(track_id)
        if status_code == 200:
            data[name] = response
        else:
            data["status"] = "failed"
            data["failure_type"] = name
            return data, status_code

    data["status"] = "success"
    data["failure_type"] = None  # type: ignore
    return data, status_code  # type: ignore


def get_audio_features():
    """This function will download the audio features from the spotify API and store them in a json file."""

    df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    path_failed = os.path.join(path_data_lake, "failed")
    number_of_files = len(os.listdir(path_data_lake))

    path_success = os.path.join(path_data_lake, "success")
    files_set = set(os.listdir(path_success))
    files_failed_set = set(os.listdir(path_success))

    retry = False

    print(f"Files to download: {len(df) - number_of_files}")

    success = 0.000001
    failed = 0

    for index, row in df.iterrows():
        if index % 1_000 == 0:  # type: ignore
            print(f"{index}/{len(df)}")

        hash = row["hash"]
        filename = f"{hash}.json"

        if filename in files_set or (filename in files_failed_set and not retry):
            continue

        track_name = row["track_name"]
        artist_name = row["artist_name"]

        data, _ = get_features(track_name, artist_name)
        data["hash"] = hash

        if data["status"] == "success":
            save_data(data, path_success, filename)
            success += 1
        else:
            save_data(data, path_failed, filename)
            failed += 1

        print(f"Success: {success}, Failed: {failed}, Ratio: {failed/success:.2f}")

        # if success > 150 and failed / success > 0.5:
        #     raise Exception("Too many failed requests")


if __name__ == "__main__":
    retries = 0
    while retries < 20:
        try:
            get_audio_features()
        except Exception as e:
            print(e)
            time.sleep(60 * 10)
            retries += 1
