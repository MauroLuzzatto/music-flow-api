import os
import time
from pprint import pprint

import pandas as pd

from music_flow.core.features.format_features import get_features
from music_flow.core.utils import path_data, path_data_lake, path_features, read_json

from concurrent.futures import ThreadPoolExecutor

def read_files_multithreaded(filenames, num_threads):
    results = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit a separate task for each file
        futures = [executor.submit(read_json, filename) for filename in filenames]

        count = 0
        # Collect the results as they become available
        for future in futures:
            result = future.result()
            results.append(result)
            count+=1

            if count % 800 == 0:  # type: ignore
                time_passed = time.time() - start
                print(f"{count}/{len(df)} - {time_passed/60.:.1f} min")

    return results


def extract_features_multithreaded(results, num_threads):
    features = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Submit a separate task for each file
        futures = [executor.submit(get_features, *result) for result in results]

        count = 0
        # Collect the results as they become available
        for future in futures:
            feature = future.result()
            features.append(feature)
            count+=1

            if count % 800 == 0:  # type: ignore
                time_passed = time.time() - start
                print(f"{count}/{len(df)} - {time_passed/60.:.1f} min")

    return features


df = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")
start = time.time()



def create_audio_features_dataset():
    """_summary_"""


    path_audio_features = os.path.join(path_features, r"audio_features_multi.csv")
    path_success = os.path.join(path_data_lake, "success")

    files_set = set(os.listdir(path_success))

    dataset = []


    df["filename"] = df["hash"].apply(lambda x: f"{x}.json")
    filenames = [
        os.path.join(path_success, filename)  for filename in df["filename"].tolist()
        if filename in files_set
    ]
    start = time.time()
    results = read_files_multithreaded(filenames, 4)
    time_passed = time.time() - start
    print(time_passed)

    inputs = [
        (result, result["track_name"], result["artist_name"], result["hash"]) for result in results
        if result["status"] != "failed"
    ]

    dataset = extract_features_multithreaded(inputs, 4)
    time_passed = time.time() - start
    print(time_passed)

    df_audio_features = pd.DataFrame(dataset)
    df_audio_features.to_csv(path_audio_features, sep=";")
    print(f"saved: {path_audio_features}")
    return df_audio_features

 






if __name__ == "__main__":
    create_audio_features_dataset()
