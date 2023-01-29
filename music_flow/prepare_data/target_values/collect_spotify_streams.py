import json
import os

import pandas as pd
from track_recommender.utils import path_data


def collect_streams():

    path = os.path.join(path_data, "raw")

    files = []
    for folder in os.listdir(path):
        path_folder = os.path.join(path, folder)
        if os.path.isdir(path_folder):
            if "MyData" in os.listdir(path_folder):
                for file in os.listdir(os.path.join(path_folder, "MyData")):
                    if "StreamingHistory" in file and "Zone" not in file:
                        files.append(os.path.join(path_folder, "MyData", file))

    full_data = []
    for file in files:
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
