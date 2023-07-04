import os

import pandas as pd

from music_flow.core.utils import path_data, path_dataset, path_features
from music_flow.dataset.config import dataset_settings

path_target_values = os.path.join(path_data, dataset_settings.TARGERT_VALUES)
path_audio_features = os.path.join(path_features, dataset_settings.AUDIO_FEATURES)
path_dataset_file = os.path.join(path_dataset, dataset_settings.FINAL_DATASET)


def create_dataset() -> pd.DataFrame:
    """Load target values and audio features and merge them into one dataset."""

    try:
        previous_dataset = pd.read_csv(path_dataset_file, sep=";", index_col=0)
        previous_rows = previous_dataset.shape[0]
    except FileNotFoundError:
        previous_rows = 0

    df_target_values = pd.read_csv(path_target_values, sep=";", index_col=0)
    df_audio_features = pd.read_csv(path_audio_features, sep=";", index_col=0)
    df_dataset = df_target_values.merge(
        df_audio_features, how="inner", on=["track_name", "artist_name"]
    )

    df_dataset.to_csv(path_dataset_file, sep=";")
    print(f"save to: {path_dataset_file}")

    print(df_dataset.head())
    print(list(df_dataset))
    print(df_dataset.shape)
    print("New rows: ", df_dataset.shape[0] - previous_rows)
    return df_dataset


if __name__ == "__main__":
    create_dataset()
