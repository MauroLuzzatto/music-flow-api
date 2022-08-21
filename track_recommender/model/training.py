import os
import sys
import pandas as pd

from xgboost import XGBRegressor  # type: ignore

from track_recommender.model.ModelClass import ModelClass, cv_settings, param_distributions
from track_recommender.utils import path, path_dataset

path_model = os.path.join(path, "results")
dataset = pd.read_csv(os.path.join(path_dataset, "dataset.csv"), sep=";", index_col = 0)


columns_scope = [
     'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
]

X = dataset[columns_scope]
y = dataset["plays"]

# train model
estimator = XGBRegressor()
model = ModelClass(estimator, X, y, path_model)
model.train(param_distributions, cv_settings)
