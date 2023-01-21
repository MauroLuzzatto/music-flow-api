import json
import os
import time
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv

from track_recommender.core.spotify_api import SpotifyAPI
from track_recommender.utils import path_data, path_data_lake, path_env

dotenv_path = os.path.join(path_env, ".env")
load_dotenv(dotenv_path)

INCLUDE_AUDIO_ANALYSIS = os.getenv("INCLUDE_AUDIO_ANALYSIS_API")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)


def save_data(data, path, filename):
    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_features(track_name: str, artist_name: str, track_id=None) -> dict:
    """ """

    data = {
        "track_name": track_name,
        "artist_name": artist_name,
    }

    if not track_id:
        is_wait = True
        while is_wait:

            url = spotify_api.search_track_url(track_name, artist_name)
            response, status_code = spotify_api.get_request(url)
            # time.sleep(1)
            if status_code == 200:
                is_wait = False
            elif status_code == 429:
                print("waiting...")
                time.sleep(60 * 3)
            else:
                data["status"] = "failed"
                data["failure_type"] = "search_track_url"
                return data

        track_id = spotify_api.get_track_id_from_response(response)

        if not track_id:
            data["status"] = "failed"
            data["failure_type"] = "track_id_from_response"
            return data

    endpoints = [
        ("audio_features", spotify_api.get_audio_features),
        ("track", spotify_api.get_track),
    ]

    if INCLUDE_AUDIO_ANALYSIS:
        endpoints.append(("audio_analysis", spotify_api.get_audio_analysis))

    for name, function_call in endpoints:

        is_wait = True
        while is_wait:
            response, status_code = function_call(track_id)
            if status_code == 200:
                data[name] = response
                is_wait = False
            elif status_code == 429:
                print("waiting...")
                time.sleep(60 * 3)
            else:
                data["status"] = "failed"
                data["failure_type"] = name
                return data

    data["status"] = "success"
    data["failure_type"] = None
    return data


def get_audio_features():

    df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    path_failed = os.path.join(path_data_lake, "failed")
    number_of_files = len(os.listdir(path_data_lake))

    files_set = set(os.listdir(path_data_lake))
    files_failed_set = set(os.listdir(path_failed))

    retry = False

    print(f"Files to download: {len(df) - number_of_files}")

    success = 0
    failed = 0

    # TODO: refactor to only load data by api request
    for index, row in df.iterrows():

        if index % 1_000 == 0:
            print(f"{index}/{len(df)}")

        hash = row["hash"]
        filename = f"{hash}.json"

        if filename in files_set or (filename in files_failed_set and not retry):
            continue

        track_name = row["track_name"]
        artist_name = row["artist_name"]

        data = get_features(track_name, artist_name)
        data["hash"] = hash

        if data["status"] == "success":
            save_data(data, path_data_lake, filename)
            success += 1
        else:
            save_data(data, path_failed, filename)
            failed += 1

        print(f"Success: {success}, Failed: {failed}")


if __name__ == "__main__":
    get_audio_features()
