import json
import logging
import os
import time
from pprint import pprint

import pandas as pd

from music_flow.core.features.get_raw_features import get_raw_features
from music_flow.core.utils import (
    path_data,
    path_data_lake_failed,
    path_data_lake_success,
)
from music_flow.config import dataset_settings

logger = logging.getLogger(__name__)

path_target_values = os.path.join(path_data, dataset_settings.TARGERT_VALUES)


def download_audio_features(is_retry_failed_files: bool = False) -> bool:
    """
    This function will download the audio features from the spotify API and store them in a json file.
    The json file will be stored in the path_data_lake folder.

    Args:
        is_retry_failed_files (bool): indicate if failed files should be retired or not

    Returns:
        bool: has_finished
    """
    df = pd.read_csv(path_target_values, sep=";")
    files_failed_set = set(os.listdir(path_data_lake_failed))
    number_of_files_failed = len(os.listdir(path_data_lake_failed))

    files_set = set(os.listdir(path_data_lake_success))
    number_of_files_success = len(os.listdir(path_data_lake_success))

    print(
        f"Files missing: {len(df) - number_of_files_failed - number_of_files_success}"
    )

    success = 0.000001
    failed = 0
    for index, row in df.iterrows():
        if index % 1_000 == 0:  # type: ignore
            print(f"{index}/{len(df)}")

        hash = row["hash"]
        filename = f"{hash}.json"

        if (
            (filename in files_set)
            or (filename in files_failed_set)
            or is_retry_failed_files
        ):
            continue

        track_name = row["track_name"]
        artist_name = row["artist_name"]

        data, status_code = get_raw_features(track_name, artist_name)
        data["hash"] = hash

        if data["status"] == "success":
            save_dict_to_json(data, path_data_lake_success, filename)
            success += 1
        else:
            save_dict_to_json(data, path_data_lake_success, filename)
            failed += 1
            logger.debug(f"{status_code} - {data}")
            print(status_code)
            pprint(data)

        print(f"Success: {int(success)}, Failed: {failed}, Ratio: {failed/success:.2f}")

        if success > 150 and failed / success > 5.0:
            raise Exception("Too many failed requests")

    return True


def save_dict_to_json(data: dict, path: str, filename: str):
    """save data to json file

    Args:
        data (dict): _description_
        path (str): _description_
        filename (str): _description_
    """
    assert filename.endswith(".json"), "filename must be a json file"

    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main(max_retries=5):
    retries = 0
    has_finished = False
    while retries < max_retries:
        try:
            has_finished = download_audio_features()
        except Exception as e:
            print(e)
            time.sleep(60 * 3)

        retries += 1
        if has_finished:
            break


if __name__ == "__main__":
    main()
