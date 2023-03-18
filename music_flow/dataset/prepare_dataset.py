import os

import pandas as pd

from music_flow.core.utils import path_data, path_dataset, path_features


def merge_dataset() -> None:
    """Load target values and audio features and merge them into one dataset."""

    previous_dataset = pd.read_csv(
        os.path.join(path_dataset, "dataset.csv"), sep=";", index_col=0
    )
    print(previous_dataset.shape)

    df_target_values = pd.read_csv(
        os.path.join(path_data, "target_values.csv"), sep=";", index_col=0
    )
    df_audio_features = pd.read_csv(
        os.path.join(path_features, "audio_features.csv"), sep=";", index_col=0
    )
    df_dataset = df_target_values.merge(
        df_audio_features, how="inner", on=["track_name", "artist_name"]
    )
    path_dataset_csv = os.path.join(path_dataset, "dataset.csv")
    df_dataset.to_csv(path_dataset_csv, sep=";")

    print(f"save to: {path_dataset_csv}")

    print(df_dataset.head())
    print(list(df_dataset))
    print(df_dataset.shape)

    print("New rows: ", df_dataset.shape[0] - previous_dataset.shape[0])


if __name__ == "__main__":
    merge_dataset()
