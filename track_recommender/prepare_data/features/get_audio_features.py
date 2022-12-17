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


def save_data(data, filename):
    with open(os.path.join(path_data_lake, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)

    df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    for index, row in df.iterrows():

        if index % 100 == 0:
            print(f"{index}/{len(df)} - {len(os.listdir(path_data_lake))}")

        track_name = row["track_name"]
        artist_name = row["artist_name"]
        hash = row["hash"]

        data = {"track_name": track_name, "artist_name": artist_name, "hash": hash}
        filename = f"{hash}.json"

        if filename in os.listdir(path_data_lake):
            continue

        url = spotify_api.search_track_url(track_name, artist_name)
        response, status_code = spotify_api.get_request(url)

        if status_code != 200:
            data["status"] = "failed"
            pprint(data)
            save_data(data, filename)
            continue

        id = spotify_api.get_track_id_from_response(response)

        if not id:
            data["status"] = "failed"
            save_data(data, filename)
            continue

        endpoints = [
            ("audio_features", spotify_api.get_audio_features),
            ("audio_analysis", spotify_api.get_audio_analysis),
            ("track", spotify_api.get_track),
        ]
        for name, function in endpoints:

            response, status_code = function(id)

            if status_code != 200:
                continue

            data[name] = response

        data["status"] = "success"
        save_data(data, filename)
