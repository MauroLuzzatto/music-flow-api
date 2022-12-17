import hashlib
import json
import os
import time
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv

from track_recommender.core.spotify_api import SpotifyAPI
from track_recommender.utils import (
    get_hash,
    path_data,
    path_data_lake,
    path_env,
    path_features,
)

dotenv_path = os.path.join(path_env, ".env")
load_dotenv(dotenv_path)


if __name__ == "__main__":

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)

    df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    failing_tracks = 0
    dataset = []

    for index, row in df.iterrows():

        if index % 100 == 0:
            print(f"{index}/{len(df)} - {len(os.listdir(path_data_lake))}")

        track_name = row["track_name"]
        artist_name = row["artist_name"]
        hash = row["hash"]

        filename = f"{hash}.json"

        try:
            with open(
                os.path.join(path_data_lake, filename), "r", encoding="utf-8"
            ) as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"File not found: {filename}")
            continue

        if data["status"] == "failed":
            failing_tracks += 1
            continue

        try:
            audio_features = data["audio_features"]
            track = data["track"]

            audio_features["track_name"] = track_name
            audio_features["artist_name"] = artist_name

            duration_ms = track["duration_ms"]
            album = track["album"]["name"]
            release_date = track["album"]["release_date"]

            explicit = track["explicit"]
            popularity = track["popularity"]
            type = track["type"]
            isrc = track["external_ids"]["isrc"]

        except KeyError as e:
            print(e)
            pprint(data["track_name"])
            os.remove(os.path.join(path_data_lake, filename))
            continue

        track_dict = {
            "id_hash": hash,
            "album": album,
            "release_date": release_date,
            "duration_ms": duration_ms,
            "explicit": explicit,
            "popularity": popularity,
            "type": type,
            "isrc": isrc,
        }

        audio_features.update(track_dict)
        # audio_features.update(audio_analysis["track"])

        dataset.append(audio_features)


df_save = pd.DataFrame(dataset)
df_save.to_csv(os.path.join(path_features, r"audio_features.csv"), sep=";")
