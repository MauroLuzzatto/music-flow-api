import hashlib
import json
import os
import time
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv
from spotify_api import SpotifyAPI

from track_recommender.utils import path_data, path_data_lake, path_env, path_features

dotenv_path = os.path.join(path_env, ".env")
load_dotenv(dotenv_path)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


if __name__ == "__main__":

    spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)

    df_streams = pd.read_csv(os.path.join(path_data, "streams.csv"))
    df = df_streams.drop_duplicates(
        subset=["trackName", "artistName"], keep="first"
    ).reset_index()

    for index, row in df.iterrows():

        if index % 100 == 100:
            print(f"{index}/{len(df)} - {len(os.listdir(path_data_lake))}")

        track_name = row["trackName"]
        artist_name = row["artistName"]

        name = f"{track_name}-{artist_name}"
        hash = get_hash(name)

        data = {"track_name": track_name, "artist_name": artist_name, "hash": hash}

        filename = f"{hash}.json"

        if filename in os.listdir(path_data_lake):
            continue

        url = spotify_api.search_track_url(track_name, artist_name)
        response, status_code = spotify_api.get_request(url)

        if status_code != 200:
            data["status"] = "failed"
            pprint(data)
            continue

        id = spotify_api.get_track_id(response)
        if id:

            data["status"] = "success"

            endpoints = [
                ("audio_features", spotify_api.get_audio_features),
                ("audio_analysis", spotify_api.get_audio_analysis),
                ("track", spotify_api.get_track),
            ]
            for name, func in endpoints:

                response, status_code = func(id)

                if status_code != 200:
                    continue

                data[name] = response

        else:
            data["status"] = "failed"

        with open(os.path.join(path_data_lake, filename), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
