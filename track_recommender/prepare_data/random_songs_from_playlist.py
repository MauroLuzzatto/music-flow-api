import os
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv

from track_recommender.core.spotify_api import SpotifyAPI
from track_recommender.utils import path_data

dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
load_dotenv(dotenv_path)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

print(CLIENT_ID, CLIENT_SECRET)
USER_ID = 1157239771
# playlist_id = "6KOwiWg5zwrt83nEcx7HyI"
# playlist_id = "37i9dQZF1DXbTxeAdrVG2l"

random_playlists = ["6p21dRudS9FmcyGvKWPq2R"]  # , "3ldvCZiQqreYp7sEuqQ6uO"


spotifAPI = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)

tracks = []

for playlist_id in random_playlists:

    for offset in range(30):

        paylist, status_code = spotifAPI.get_playlist_items(
            playlist_id=playlist_id, limit=1, offset=offset
        )

        print([track["track"]["name"] for track in paylist["items"]])
        print(len(paylist["items"]))

        if len(paylist["items"]) == 0:
            continue

        for track in paylist["items"]:
            print("---" * 5)

            # from pprint import pprint
            # pprint(track)

            try:
                artists = [artist["name"] for artist in track["track"]["artists"]][0]
            except IndexError:
                artists = None

            track_name = track["track"]["name"]
            track_id = track["track"]["id"]
            album = track["track"]["album"]["name"]
            release_date = track["track"]["album"]["release_date"]

            added_at = track["added_at"]

            duration_ms = track["track"]["duration_ms"]
            explicit = track["track"]["explicit"]
            popularity = track["track"]["popularity"]
            type = track["track"]["type"]
            track = track["track"]["track"]

            track_dict = {
                "track_id": track_id,
                "artists": artists,
                "track_name": track_name,
                "album": album,
                "release_date": release_date,
                "added_at": added_at,
                "duration_ms": duration_ms,
                "explicit": explicit,
                "popularity": popularity,
                "type": type,
                "track": track,
            }
            tracks.append(track_dict)


df = (
    pd.DataFrame(tracks)
    .drop_duplicates(subset=["track_name", "artists"], keep="last")
    .reset_index(drop=True)
)

print(df)
df.to_csv(os.path.join(path_data, "random_tracks.csv"), sep=";", header=False, mode="a")
