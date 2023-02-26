import json
import os

import pandas as pd

from music_flow.core.utils import path_data


def collect_streams():
    path = os.path.join(path_data, "raw")

    output = []

    for root, _, files in os.walk(path):
        for file in files:
            if "StreamingHistory" in file and "Zone" not in file:
                output.append(os.path.join(root, file))

    full_data = []
    for file in output:
        print(file)
        with open(file, mode="r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        full_data.extend(data)

    df = pd.DataFrame(full_data)
    df.to_csv(os.path.join(path_data, "streams.csv"), sep=";")
    path = os.path.join(path_data, "streams.csv")
    print(f"save to: {path}")


if __name__ == "__main__":
    collect_streams()
