import os
import sys

import numpy as np
import pandas as pd
from pandas_profiling import ProfileReport
from xgboost import XGBRegressor  # type: ignore

from track_recommender.model.ModelClass import ModelClass
from track_recommender.utils import path, path_dataset

make_report = False

path_model = os.path.join(path, "results")
path_reports = os.path.join(path, "reports")
dataset = pd.read_csv(os.path.join(path_dataset, "dataset.csv"), sep=";", index_col=0)


# transformation step
for column in ["plays", "speechiness", "acousticness", "instrumentalness", "liveness"]:
    dataset[column] = dataset[column].apply(np.log1p)


# feature engineering
# - us np.log1 for skewed variables like instrumentalness
# https://www.kaggle.com/general/93016


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


def get_one_hot_encoding(df, column):
    """
    convert list of features into one hot encoded values
    """
    df_one_hot = pd.get_dummies(df[column])
    df = df.drop(column, axis=1)
    df = df.join(df_one_hot)
    return df


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


def map_keys_to_string(row):
    try:
        key = key_mapping[int(row)]
    except ValueError:
        key = "Unknown"
    return key


dataset["key"] = dataset["key"].apply(map_keys_to_string)

# key is a categorical variable
dataset = get_one_hot_encoding(dataset, column="key")


if make_report:
    profile = ProfileReport(dataset, title="Pandas Profiling Report", explorative=True)
    profile.to_file(os.path.join(path_reports, "dataset_report.html"))


columns_scope.extend(list(key_mapping.values()))

X = dataset[columns_scope]
y = dataset["plays"]

# train model
estimator = XGBRegressor()
model = ModelClass(estimator, X, y, path_model)


param_distributions = {
    "learning_rate": [0.001, 0.01, 0.1, 0.25],
    "max_depth": [3, 5, 7],
    "min_child_weight": [1, 3, 5],
    "subsample": [0.5, 0.8, 1.0],
    "colsample_bytree": [0.25, 0.5, 0.7],
    "n_estimators": [100, 200],
    "objective": ["reg:squarederror"],
}

cv_settings = {
    "n_iter": 20,  # total combinations testes
    "scoring": "r2",
    "cv": 3,
    "random_state": 0,
    "n_jobs": -1,
    "verbose": 3,
}

model.train(param_distributions, cv_settings)
