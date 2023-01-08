import os

import pandas as pd

from track_recommender.utils import path_data

df_kaggle = (
    (
        pd.read_csv(
            os.path.join(path_data, "kaggle", "kaggle_spotify_dataset", "tracks.csv"),
            index_col=0,
            usecols=["name", "artists"],
        )
    )
    .drop_duplicates(keep="first")
    .reset_index()
)

df_kaggle.rename(columns={"artists": "artist_name", "name": "track_name"}, inplace=True)
df_kaggle["artist_name"] = df_kaggle["artist_name"].apply(
    lambda row: row[2:-2].split(",")[0]
)
df_kaggle = df_kaggle.drop_duplicates(
    subset=["artist_name", "track_name"], keep="first"
)
df_kaggle = df_kaggle.head(40_000)

path = os.path.join(path_data, "kaggle_tracks.csv")
df_kaggle.to_csv(path, sep=";")
print(f"save to: {path}")
print(df_kaggle.shape)
