import os

import pandas as pd

from music_flow.config import dataset_settings, settings
from music_flow.core.utils import get_hash, path_data

path_target_values = os.path.join(path_data, dataset_settings.TARGERT_VALUES)
path_raw_streams = os.path.join(path_data, dataset_settings.RAW_STREAMS)
path_kaggle_tracks = os.path.join(path_data, dataset_settings.KAGGEL_DATASET)


def get_stream_data() -> pd.DataFrame:
    """aggregate the raw streams to counts per track

    Returns:
        pd.DataFrame: return a dataframe with the number of streams per track
    """
    columns = {
        "artistName": "artist_name",
        "trackName": "track_name",
        "endTime": "end_time",
    }

    df = pd.read_csv(
        path_raw_streams,
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


def get_kaggle_data() -> pd.DataFrame:
    """load a list of tracks form a dataset from Kaggle
    https://www.kaggle.com/datasets/mrmorj/dataset-of-songs-in-spotify

    Returns:
        pd.DataFrame: dataframe with a list of tracks
    """
    df_kaggle = (
        (
            pd.read_csv(
                path_kaggle_tracks,
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


def create_target_values(include_kaggle: bool = True) -> pd.DataFrame:
    """Combine the downloaded stream data to a target dataframe with number of play
    per track

    Args:
        include_kaggle (bool, optional): Include tracks from the Kaggle dataset. Defaults to True.

    Returns:
        pd.DataFrame: dataframe with number of plays per track from streams and kaggle data
    """
    list_of_dfs = []
    df_streams = get_stream_data()
    df_streams["source"] = "streams"
    print("df_streams", df_streams.shape)
    list_of_dfs.append(df_streams)

    if include_kaggle:
        try:
            df_kaggle = get_kaggle_data()
            df_kaggle["source"] = "kaggle"
            print("df_kaggle", df_kaggle.shape)
            list_of_dfs.append(df_kaggle)
        except FileNotFoundError:
            pass

    df = pd.concat(list_of_dfs, axis=0).reset_index(drop=True)
    print("df_target_values", df.shape)

    df["hash"] = df.apply(
        lambda row: get_hash(f"{row['track_name']}-{row['artist_name']}"), axis=1
    )
    df_target_values = df.drop_duplicates(subset=["hash"], keep="first")
    print("df_target_values (dropped duplicates)", df_target_values.shape)

    df_target_values.to_csv(path_target_values, sep=";")
    print(f"save to: {path_target_values}")
    print(df_target_values.shape)
    return df_target_values


if __name__ == "__main__":
    create_target_values()
