import os

import pandas as pd

from music_flow.config import dataset_settings
from music_flow.core.utils import path_data

path_kaggle = os.path.join(path_data, "kaggle", "kaggle_spotify_dataset", "tracks.csv")
path_kaggle_dataset = os.path.join(path_data, dataset_settings.KAGGEL_DATASET)

if __name__ == "__main__":
    df_kaggle = (
        (
            pd.read_csv(
                path_kaggle,
                index_col=0,
                usecols=["name", "artists"],
            )
        )
        .drop_duplicates(keep="first")
        .reset_index()
    )

    df_kaggle.rename(
        columns={"artists": "artist_name", "name": "track_name"}, inplace=True
    )
    df_kaggle["artist_name"] = df_kaggle["artist_name"].apply(
        lambda row: row[2:-2].split(",")[0]
    )
    df_kaggle = df_kaggle.drop_duplicates(
        subset=["artist_name", "track_name"], keep="first"
    )

    df_kaggle.to_csv(path_kaggle_dataset, sep=";")
    print(f"save to: {path_kaggle}")
    print(df_kaggle.shape)
