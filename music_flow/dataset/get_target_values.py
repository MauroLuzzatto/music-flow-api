import os

import pandas as pd

from music_flow.config.core import settings
from music_flow.core.utils import get_hash, path_data


def get_df_streams():
    columns = {
        "artistName": "artist_name",
        "trackName": "track_name",
        "endTime": "end_time",
    }

    df = pd.read_csv(
        os.path.join(path_data, "streams.csv"),
        sep=";",
        usecols=["artistName", "trackName", "endTime"],
    ).rename(columns=columns)

    df["end_time"] = pd.to_datetime(df["end_time"])
    print(df.shape)
    df.drop_duplicates(subset=["end_time", "track_name", "artist_name"], inplace=True)
    print(df.shape)

    df_streams = (
        df.groupby(["artist_name", "track_name"])
        .size()
        .reset_index()
        .rename(columns={0: "plays"})
    )
    return df_streams


def get_df_random():
    columns = {"artists": "artist_name"}

    df_random = (
        (
            pd.read_csv(
                os.path.join(path_data, "random_tracks.csv"),
                sep=";",
                index_col=0,
                usecols=["artists", "track_name"],
            )
        )
        .drop_duplicates(keep="first")
        .reset_index()
    ).rename(columns=columns)
    df_random["plays"] = 0
    return df_random


def get_df_kaggle():
    df_kaggle = (
        (
            pd.read_csv(
                os.path.join(path_data, "kaggle_tracks.csv"),
                sep=";",
                index_col=0,
                usecols=["artist_name", "track_name"],
            )
        )
        .drop_duplicates(keep="first")
        .reset_index()
    ).head(settings.NUMBER_OF_KAGGLE_DATASET_TRACKS)

    df_kaggle["plays"] = 0
    return df_kaggle


def get_df_target_values(include_kaggle=True, include_random=True):
    list_of_dfs = []

    df_streams = get_df_streams()
    df_streams["source"] = "streams"
    print("df_streams", df_streams.shape)
    list_of_dfs.append(df_streams)

    if include_random:
        df_random = get_df_random()
        df_random["source"] = "random"
        print("df_random", df_random.shape)
        list_of_dfs.append(df_random)

    if include_kaggle:
        df_kaggle = get_df_kaggle()
        df_kaggle["source"] = "kaggle"
        print("df_kaggle", df_kaggle.shape)
        list_of_dfs.append(df_kaggle)

    df = pd.concat(list_of_dfs, axis=0).reset_index(drop=True)

    print("df_target_values", df.shape)

    df["hash"] = df.apply(
        lambda row: get_hash(f"{row['track_name']}-{row['artist_name']}"), axis=1
    )
    df_target_values = df.drop_duplicates(subset=["hash"], keep="first")
    print("df_target_values (dropped duplicates)", df_target_values.shape)

    path_target_values_csv = os.path.join(path_data, "target_values.csv")
    df_target_values.to_csv(path_target_values_csv, sep=";")
    print(f"save to: {path_target_values_csv}")
    print(df_target_values.shape)
    return df_target_values


if __name__ == "__main__":
    get_df_target_values()
