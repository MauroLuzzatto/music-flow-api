from music_flow.core.utils import path_dataset, create_folder, path_results
import json
import os
import pandas as pd


results = []


def read_json(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, NotADirectoryError):
        data = {}
    return data


for folder in os.listdir(path_results):
    path = os.path.join(path_results, folder)
    print(path)
    if not os.path.isdir(path):
        continue

    files = os.listdir(path)

    if "score_dict.json" in files:
        path = os.path.join(path_results, folder, "score_dict.json")
        score_dict = read_json(path)

    elif "metadata.json" in files:
        path = os.path.join(path_results, folder, "metadata.json")
        metadata = read_json(path)
        key = "score" if "score" in metadata["model"] else "score_dict"
        score_dict = metadata["model"].get(key, {})

    score_dict["folder"] = folder
    results.append(score_dict)


df = pd.DataFrame(results).sort_values("mean_squared_error")
df.to_csv(os.path.join(path_results, "results_overview.csv"))
print(df)
