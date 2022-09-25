import os

import pandas as pd

from track_recommender.utils import (
    path_data,
    path_data_lake,
    path_dataset,
    path_env,
    path_features,
)

df = pd.read_csv(
    os.path.join(path_data, "streams.csv"), sep=";", usecols=["artistName", "trackName"]
)

df_audio_features = pd.read_csv(
    os.path.join(path_features, "audio_features.csv"), sep=";", index_col=0
)


df.rename(
    columns={"artistName": "artist_name", "trackName": "track_name"}, inplace=True
)
df_target_values = (
    df.groupby(["artist_name", "track_name"])
    .size()
    .reset_index()
    .rename(columns={0: "plays"})
)

df_dataset = df_target_values.merge(
    df_audio_features, how="inner", on=["track_name", "artist_name"]
)
df_dataset.to_csv(os.path.join(path_dataset, "dataset.csv"), sep=";")


print(list(df_dataset))
