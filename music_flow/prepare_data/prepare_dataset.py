import os

import pandas as pd

from music_flow.utils import path_data, path_dataset, path_features


def get_dataset() -> None:
    """_summary_"""

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


if __name__ == "__main__":
    get_dataset()
