import os
import sys
import pandas as pd

from xgboost import XGBRegressor  # type: ignore

sys.path.insert(
    0,
    r"/home/maurol/track-recommender",
)

from track_recommender.model.ModelClass import ModelClass, cv_settings, param_distributions

path_base = r"/home/maurol/track-recommender"
path_data = os.path.join(path_base, "data", "dataset")
path_model = os.path.join(path_base, "model_artifact")


dataset = pd.read_csv(r"/home/maurol/track-recommender/data/datasest/dataset.csv", sep=";", index_col = 0)

columns_scope = list(dataset.select_dtypes(exclude=['object']).columns)
print(columns_scope)

columns_scope = [
     'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
]

X = dataset[columns_scope]
y = dataset["plays"]

# train model
estimator = XGBRegressor()
model = ModelClass(estimator, X, y, path_model, folder="output")
model.train(param_distributions, cv_settings)
