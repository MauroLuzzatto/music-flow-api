import os

import pandas as pd

from track_recommender.utils import path_data, path_dataset, path_features

df_target_values = pd.read_csv(os.path.join(path_data, "target_values.csv"), sep=";")

df_audio_features = pd.read_csv(
    os.path.join(path_features, "audio_features.csv"), sep=";", index_col=0
)


df_dataset = df_target_values.merge(
    df_audio_features, how="inner", on=["track_name", "artist_name"]
)
df_dataset.to_csv(os.path.join(path_dataset, "dataset.csv"), sep=";")

print(df_dataset)
