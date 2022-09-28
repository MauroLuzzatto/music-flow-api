import os
import sys

import pandas as pd
from xgboost import XGBRegressor  # type: ignore

from track_recommender.model.ModelClass import ModelClass
from track_recommender.utils import path, path_dataset

path_model = os.path.join(path, "results")
dataset = pd.read_csv(os.path.join(path_dataset, "dataset.csv"), sep=";", index_col=0)


columns_scope = [
    "danceability",
    "energy",
    "key",
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
