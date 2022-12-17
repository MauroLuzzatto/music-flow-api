import os

import pandas as pd

from track_recommender.utils import get_hash, path_data


def main():

    df = pd.read_csv(
        os.path.join(path_data, "streams.csv"),
        sep=";",
        usecols=["artistName", "trackName", "endTime"],
    ).rename(
        columns={
            "artistName": "artist_name",
            "trackName": "track_name",
            "endTime": "end_time",
        }
    )

    df["end_time"] = pd.to_datetime(df["end_time"])

    print(df.shape)
    df.drop_duplicates(subset=["end_time", "track_name", "artist_name"], inplace=True)
    print(df.shape)

    df_target_values = (
        df.groupby(["artist_name", "track_name"])
        .size()
        .reset_index()
        .rename(columns={0: "plays"})
    )
    df_random = (
        (
            pd.read_csv(
                os.path.join(path_data, "random_tracks.csv"),
                sep=";",
                index_col=0,
                usecols=["artists", "track_name"],
            )
        )
        .drop_duplicates(keep="first")
        .reset_index()
    )
    df_random.rename(columns={"artists": "artist_name"}, inplace=True)
    df_random["plays"] = 0
    df_target_values = pd.concat([df_target_values, df_random], axis=0).reset_index(
        drop=True
    )
    df_target_values["hash"] = df_target_values.apply(
        lambda row: get_hash(f"{row['track_name']}-{row['artist_name']}"), axis=1
    )
    path = os.path.join(path_data, "target_values.csv")
    df_target_values.to_csv(path, sep=";")
    print(f"save to: {path}")
    return df_target_values


if __name__ == "__main__":
    main()
