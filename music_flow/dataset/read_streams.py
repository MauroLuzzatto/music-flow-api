import json
import os

import pandas as pd

from music_flow.core.utils import path_data
from music_flow.dataset.config import dataset_settings

path_raw = os.path.join(path_data, "raw")
path_save = os.path.join(path_data, dataset_settings.RAW_STREAMS)


def read_streams() -> pd.DataFrame:
    """extract the streams from the StreamingHistory file

    Returns:
        pd.DataFrame: DataFrame with all streams
    """
    output = []
    for root, _, files in os.walk(path_raw):
        for file in files:
            if "StreamingHistory" in file and "Zone" not in file:
                output.append(os.path.join(root, file))

    full_data = []
    for file in output:
        print(file)
        with open(file, mode="r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        full_data.extend(data)

    df_streams = pd.DataFrame(full_data)
    df_streams.to_csv(path_save, sep=";")
    print(f"save to: {path_save}")
    return df_streams


if __name__ == "__main__":
    read_streams()
