import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from utils import path, path_features

df = pd.read_csv(os.path.join(path_features, "streams.csv"), sep=";", index_col=0)

# df_audio_features = df.drop_duplicates(subset=["track", "artist"], keep="first")

# print(list(df))

# number_of_tracks = len(df)
# number_of_unique_tracks = len(df.groupby(["track", "artist"]))
# number_of_artist = df["artist"].nunique()
# duration_ms = df["ms_played"].sum()
# print(number_of_tracks)
# print(number_of_unique_tracks)
# print(number_of_artist)
# print(duration_ms)

df_target_values = (
    df.groupby(["track", "artist"]).size().reset_index().rename(columns={0: "plays"})
)
# plays_per_artist = counts_per_track.groupby(['artist'])['counts'].sum().reset_index().rename(columns={0:'plays_per_artist'})


df_target_values.to_csv("target_values.csv", sep=";")


exit()


dataset = df_counts_per_track.merge(
    df_audio_features, how="left", on=["track", "artist"]
)
dataset.drop(
    columns=["error", "end_time", "ms_played", "track_href", "analysis_url", "type"],
    inplace=True,
)

print(dataset.shape)
dataset.to_csv("dataset.csv", sep=";")


# df_plot = counts_per_track.sort_values("counts", ascending=False).head(10)
# print(df_plot)

# fig = px.bar(df_plot, x="artist", y="counts", color = "track", height=800)
# fig.show()
