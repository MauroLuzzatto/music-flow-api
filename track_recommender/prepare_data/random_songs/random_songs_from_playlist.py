import os
from pprint import pprint

import pandas as pd
from dotenv import load_dotenv

from track_recommender.core.spotify_api import SpotifyAPI
from track_recommender.prepare_data.get_playlist_tracks import get_playlist_tracks
from track_recommender.utils import path_data

dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
load_dotenv(dotenv_path)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

USER_ID = 1157239771
# playlist_id = "6KOwiWg5zwrt83nEcx7HyI"
# playlist_id = "37i9dQZF1DXbTxeAdrVG2l"

random_playlists = ["6p21dRudS9FmcyGvKWPq2R"]  # , "3ldvCZiQqreYp7sEuqQ6uO"
spotifAPI = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)


if __name__ == "__main__":
    list_of_tracks = []

    for playlist_id in random_playlists:
        paylist, status_code = spotifAPI.get_playlist_items(playlist_id=playlist_id)
        tracks = get_playlist_tracks(paylist)
        list_of_tracks.extend(tracks)

    df = (
        pd.DataFrame(list_of_tracks)
        .drop_duplicates(subset=["track_name", "artists"], keep="last")
        .reset_index(drop=True)
    )

    print(df)
    df.to_csv(
        os.path.join(path_data, "random_tracks.csv"), sep=";", header=False, mode="a"
    )
