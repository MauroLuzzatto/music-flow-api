import json
import os
import time
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv

from track_recommender.utils import path_data, path_data_lake, path_env, path_features

dotenv_path = os.path.join(path_env, ".env")
load_dotenv(dotenv_path)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def format_features(data, track_name, artist_name, hash=None):
    """
    TODO: update function
    """

    try:
        audio_features = data["audio_features"]
    except KeyError as e:
        print(e)
        return {}

    try:
        track = data["track"]
    except KeyError as e:
        print(e)
        return {}

    audio_features["track_name"] = track_name
    audio_features["artist_name"] = artist_name

    try:
        duration_ms = track["duration_ms"]
        album = track["album"]["name"]
        release_date = track["album"]["release_date"]
        explicit = track["explicit"]
        popularity = track["popularity"]
        type = track["type"]
        isrc = track["external_ids"]["isrc"]
    except KeyError as e:
        print(e)
        return {}

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
    return audio_features


def create_audio_features_dataset():

    df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    failing_tracks = 0
    dataset = []
    start = time.time()
    for index, row in df.iterrows():

        if index % 10_000 == 0:
            time_passed = time.time() - start
            print(f"{index}/{len(df)} - {time_passed/60.:.1f} min")

        track_name = row["track_name"]
        artist_name = row["artist_name"]
        hash = row["hash"]
        filename = f"{hash}.json"

        try:
            path = os.path.join(path_data_lake, filename)
            data = load_json(path)
        except FileNotFoundError:
            print(f"File not found: {filename}")
            continue

        if data["status"] == "failed":
            failing_tracks += 1
            os.remove(os.path.join(path_data_lake, filename))
            continue

        audio_features = format_features(data, track_name, artist_name, hash)

        if not audio_features:
            pprint(data["track_name"])
            os.remove(os.path.join(path_data_lake, filename))
            continue

        # audio_features.update(audio_analysis["track"])
        dataset.append(audio_features)

    df_audio_features = pd.DataFrame(dataset)
    path = os.path.join(path_features, r"audio_features.csv")
    df_audio_features.to_csv(path, sep=";")
    print(f"saved: {path}")


if __name__ == "__main__":
    create_audio_features_dataset()
