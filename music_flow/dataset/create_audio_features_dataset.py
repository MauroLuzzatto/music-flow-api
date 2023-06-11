import os
import time
from pprint import pprint

import pandas as pd

from music_flow.core.features.format_features import get_features
from music_flow.core.utils import (
    path_data,
    path_features,
    read_json,
    path_data_lake_success,
)
from music_flow.dataset.config import dataset_settings

path_target_values = os.path.join(path_data, dataset_settings.TARGERT_VALUES)
path_audio_features = os.path.join(path_features, dataset_settings.AUDIO_FEATURES)


def create_audio_features_dataset():
    """Create the audio features dataset"""

    df = pd.read_csv(path_target_values, sep=";")
    files_set = set(os.listdir(path_data_lake_success))
    count_failing_tracks = 0
    count_missing_tracks = 0

    dataset = []
    start = time.time()
    for index, row in df.iterrows():
        if int(index) % 800 == 0:  # type: ignore
            time_passed = time.time() - start
            print(f"{index}/{len(df)} - {time_passed/60.:.1f} min")
            print(
                f"missing tracks: {count_missing_tracks} - failing tracks:"
                f" {count_failing_tracks}"
            )

        track_name = row["track_name"]
        artist_name = row["artist_name"]
        hash = row["hash"]
        filename = f"{hash}.json"

        if filename not in files_set:
            count_missing_tracks += 1
            continue

        path_file = os.path.join(path_data_lake_success, filename)
        data = read_json(path_file)

        if (
            data["status"] == "failed"
            and not data["failure_reason"] == "audio_analysis"
        ):
            count_failing_tracks += 1
            pprint(data["track_name"])
            os.remove(path_file)
            continue

        features = get_features(data, track_name, artist_name, hash)

        if not features:
            count_failing_tracks += 1
            pprint(data["track_name"])
            os.remove(path_file)
            continue

        dataset.append(features)

    df_audio_features = pd.DataFrame(dataset)
    df_audio_features.to_csv(path_audio_features, sep=";")
    print(f"saved: {path_audio_features}")
    return df_audio_features


if __name__ == "__main__":
    create_audio_features_dataset()
