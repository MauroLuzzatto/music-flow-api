import os

import pandas as pd

from music_flow.core.get_playlist_tracks import get_playlist_tracks
from music_flow.core.spotify_api import SpotifyAPI
from music_flow.core.utils import path_data

random_playlists = ["6p21dRudS9FmcyGvKWPq2R"]

spotify_api = SpotifyAPI()


if __name__ == "__main__":
    list_of_tracks = []

    for playlist_id in random_playlists:
        paylist, status_code = spotify_api.get_playlist_items(playlist_id=playlist_id)
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
