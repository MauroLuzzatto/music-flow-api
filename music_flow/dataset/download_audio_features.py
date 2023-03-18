import json
import logging
import logging.config
import os
import time

import pandas as pd

from music_flow.core.features.get_audio_features import get_raw_features
from music_flow.core.utils import path_data, path_data_lake

logger = logging.getLogger(__name__)


def save_dict_to_json(data: dict, path: str, filename: str):
    assert filename.endswith(".json"), "filename must be a json file"

    with open(os.path.join(path, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def download_audio_features(df=None):
    """This function will download the audio features from the spotify API and store them in a json file.
    """
    retry = False

    if not df:
        df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

    path_failed = os.path.join(path_data_lake, "failed")
    number_of_files = len(os.listdir(path_data_lake))

    path_success = os.path.join(path_data_lake, "success")
    files_set = set(os.listdir(path_success))
    files_failed_set = set(os.listdir(path_success))

    print(f"Files to download: {len(df) - number_of_files}")

    success = 0.000001
    failed = 0

    for index, row in df.iterrows():
        if index % 1_000 == 0:  # type: ignore
            print(f"{index}/{len(df)}")

        hash = row["hash"]
        filename = f"{hash}.json"

        if filename in files_set or (filename in files_failed_set and not retry):
            continue

        track_name = row["track_name"]
        artist_name = row["artist_name"]

        data, _ = get_raw_features(track_name, artist_name)
        data["hash"] = hash

        if data["status"] == "success":
            save_dict_to_json(data, path_success, filename)
            success += 1
        else:
            save_dict_to_json(data, path_failed, filename)
            failed += 1

        print(f"Success: {success}, Failed: {failed}, Ratio: {failed/success:.2f}")

        if success > 150 and failed / success > 5.0:
            raise Exception("Too many failed requests")


def main(max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
            download_audio_features()
        except Exception as e:
            print(e)
            time.sleep(60 * 10)
            retries += 1


if __name__ == "__main__":
    main()
