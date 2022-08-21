import hashlib
import json
import os

import pandas as pd
from dotenv import load_dotenv
from spotify_api import SpotifyAPI

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


track = "one more time"
artist = "daft punk"


def get_hash(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


if __name__ == "__main__":

    spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
    df = pd.read_csv("streams.csv")

    cache = {}
    failing_tracks = []
    dataset = []

    for index, row in df.iterrows():

        if index % 10000 == 0 and index > 0:
            df_save = pd.DataFrame(dataset)
            df_save.to_csv(f"audio_features_{index}.csv", sep=";")

        print(f"{index}/{len(df)} - {len(cache)}")
        track = row["trackName"]
        artist = row["artistName"]

        name = f"{track}-{artist}"
        hash = get_hash(name)
        if hash in cache:
            dataset.append(cache[hash])
            continue

        url = spotify_api.search_track_url(track, artist)
        r = spotify_api.get_request(url)
        id = spotify_api.get_track_id(r)

        if id:
            url = spotify_api.get_audio_features_url(id)
            audio_features = spotify_api.get_request(url)

            audio_features["ms_played"] = row["msPlayed"]
            audio_features["end_time"] = row["endTime"]
            audio_features["track"] = track
            audio_features["artist"] = artist

            # audio_analysis = spotifAPI.get_audio_analysis(id)

            # print(audio_analysis)
            # print(audio_features)

            dataset.append(audio_features)
            cache[hash] = audio_features
        else:
            failing_tracks.append((track, artist))


df_save = pd.DataFrame(dataset)
df_save.to_csv(r"audio_features.csv", sep=";")
