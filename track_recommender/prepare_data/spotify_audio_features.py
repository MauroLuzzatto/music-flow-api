import hashlib
import json
import os
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv
from spotify_api import SpotifyAPI

from track_recommender.utils import path_env, path_data

dotenv_path = os.path.join(path_env, ".env")
load_dotenv(dotenv_path)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


track = "one more time"
artist = "daft punk"


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


if __name__ == "__main__":

    spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
    df = pd.read_csv(os.path.join(path_data, "streams.csv"))

    cache = {}
    failing_tracks = []
    dataset = []

    for index, row in df.iterrows():

        if index % 10000 == 0 and index > 0:
            df_save = pd.DataFrame(dataset)
            df_save.to_csv(f"audio_features_{index}.csv", sep=";")

        print(f"{index}/{len(df)} - {len(cache)}")
        track_name = row["trackName"]
        artist_name = row["artistName"]

        name = f"{track_name}-{artist_name}"
        hash = get_hash(name)
        if hash in cache:
            dataset.append(cache[hash])
            continue

        url = spotify_api.search_track_url(track_name, artist_name)
        r = spotify_api.get_request(url)
        id = spotify_api.get_track_id(r)

        if id:
            audio_features = spotify_api.get_audio_features(id)
            audio_analysis = spotify_api.get_audio_analysis(id)
            track = spotify_api.get_track(id)

            # audio_features["ms_played"] = row["msPlayed"]
            # audio_features["end_time"] = row["endTime"]

            for key in [
                "codestring",
                "code_version",
                "echoprintstring",
                "echoprint_version",
                "synchstring",
                "synch_version",
                "rhythmstring",
                "rhythm_version",
            ]:
                del audio_analysis["track"][key]

            audio_features["track_name"] = track_name
            audio_features["artist_name"] = artist_name

            duration_ms = track["duration_ms"]
            album = track["album"]["name"]
            release_date = track["album"]["release_date"]

            explicit = track["explicit"]
            popularity = track["popularity"]
            type = track["type"]
            isrc = track["external_ids"]["isrc"]

            track_dict = {
                "album": album,
                "release_date": release_date,
                "duration_ms": duration_ms,
                "explicit": explicit,
                "popularity": popularity,
                "type": type,
                "isrc": isrc,
            }

            audio_features.update(track_dict)
            audio_features.update(audio_analysis["track"])

            with open("data.json", "w", encoding="utf-8") as f:
                json.dump(audio_features, f, ensure_ascii=False, indent=4)

            exit()
            # print(audio_analysis)
            # print(audio_features)

            dataset.append(audio_features)
            cache[hash] = audio_features
        else:
            failing_tracks.append((track, artist))


df_save = pd.DataFrame(dataset)
df_save.to_csv(r"audio_features.csv", sep=";")
