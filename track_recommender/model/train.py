import os
import sys

import numpy as np
import pandas as pd
from pandas_profiling import ProfileReport
from xgboost import XGBRegressor  # type: ignore

from track_recommender.model.ModelClass import ModelClass
from track_recommender.model.preprocessing import feature_preprocessing
from track_recommender.utils import path, path_dataset

make_report = False

path_model = os.path.join(path, "results")
path_reports = os.path.join(path, "reports")
dataset = pd.read_csv(os.path.join(path_dataset, "dataset.csv"), sep=";", index_col=0)


dataset["plays"] = dataset["plays"].apply(lambda row: row if row < 18 else 18)
print(dataset["plays"].value_counts())

dataset, columns_scope = feature_preprocessing(dataset)

if make_report:
    profile = ProfileReport(dataset, title="Pandas Profiling Report", explorative=True)
    profile.to_file(os.path.join(path_reports, "dataset_report.html"))


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
