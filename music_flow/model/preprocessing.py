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

    drop_columns = [
        "type",
        "id",
        "uri",
        "track_href",
        "analysis_url",
        "id_hash",
        "release_date",
        "isrc",
        "album",
        "track_name",
        "artist_name",
        "release_date_precision",
    ]

    dataset.drop(columns=drop_columns, inplace=True)

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

    for column in ["key"]:
        dataset = get_one_hot_encoding(dataset, column=column)

    for col in key_mapping.values():
        if col not in dataset:
            dataset[col] = 0

    columns_scope = list(dataset)
    columns_scope.extend(list(key_mapping.values()))
    return dataset, columns_scope
