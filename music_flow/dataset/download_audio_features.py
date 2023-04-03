import json
import logging
import os
import time
from pprint import pprint

import pandas as pd

from music_flow.core.features.get_audio_features import get_raw_features
from music_flow.core.utils import path_data, path_data_lake

logger = logging.getLogger(__name__)


def save_dict_to_json(data: dict, path: str, filename: str):
    """_summary_

    Args:
        data (dict): _description_
        path (str): _description_
        filename (str): _description_
    """
    assert filename.endswith(".json"), "filename must be a json file"

    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def download_audio_features(df=None) -> bool:
    """
    This function will download the audio features from the spotify API and store them in a json file.
    The json file will be stored in the path_data_lake folder.

    Args:
        df (dict): The dataframe containing the track names and artist names.
    """
    retry_failed_files = False

    if not df:
        df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    path_failed = os.path.join(path_data_lake, "failed")
    files_failed_set = set(os.listdir(path_failed))
    number_of_files_failed = len(os.listdir(path_failed))

    path_success = os.path.join(path_data_lake, "success")
    files_set = set(os.listdir(path_success))
    number_of_files_success = len(os.listdir(path_success))

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

        if (filename in files_set) or (
            filename in files_failed_set or retry_failed_files
        ):
            continue

        track_name = row["track_name"]
        artist_name = row["artist_name"]

        data, status_code = get_raw_features(track_name, artist_name)
        data["hash"] = hash

        if data["status"] == "success":
            save_dict_to_json(data, path_success, filename)
            success += 1
        else:
            save_dict_to_json(data, path_failed, filename)
            failed += 1
            logger.debug(f"{status_code} - {data}")
            print(status_code)
            pprint(data)

        print(f"Success: {int(success)}, Failed: {failed}, Ratio: {failed/success:.2f}")

        if success > 150 and failed / success > 5.0:
            raise Exception("Too many failed requests")

    return True


def main(max_retries=5):
    retries = 0
    has_finished = False
    while retries < max_retries or not has_finished:
        try:
            has_finished = download_audio_features()
        except Exception as e:
            print(e)
            time.sleep(60 * 3)

        retries += 1


if __name__ == "__main__":
    main()
