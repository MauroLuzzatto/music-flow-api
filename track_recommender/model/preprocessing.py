import numpy as np
import pandas as pd

key_mapping = {
    0: "C",
    1: "C#/Db",
    2: "D",
    3: "D#/Eb",
    4: "E",
    5: "F",
    6: "F#/Gb",
    7: "G",
    8: "G#/Ab",
    9: "A",
    10: "A#/Bb",
    11: "B",
}


def get_one_hot_encoding(df, column):
    """
    convert list of features into one hot encoded values
    """
    df_one_hot = pd.get_dummies(df[column])
    df = df.drop(column, axis=1)
    df = df.join(df_one_hot)
    return df


def map_keys_to_string(row):
    try:
        key = key_mapping[int(row)]
    except ValueError:
        key = "Unknown"
    return key


def reverse_prediction(value):
    return np.expm1(value)


def feature_preprocessing(dataset: pd.DataFrame):

    # transformation step
    for column in [
        "plays",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
    ]:
        dataset[column] = dataset[column].apply(np.log1p)

    # feature engineering
    # - us np.log1 for skewed variables like instrumentalness
    # https://www.kaggle.com/general/93016

    dataset["key"] = dataset["key"].apply(map_keys_to_string)
    # key is a categorical variable
    dataset = get_one_hot_encoding(dataset, column="key")

    for col in key_mapping.values():
        if col not in dataset:
            dataset[col] = 0

    columns_scope = [
        "danceability",
        "energy",
        # "key",
        "loudness",
        "mode",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "duration_ms",
        "time_signature",
        "explicit",
        "popularity",
    ]

    columns_scope.extend(list(key_mapping.values()))
    return dataset, columns_scope
