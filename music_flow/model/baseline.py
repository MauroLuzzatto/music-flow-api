import os

import pandas as pd
from xgboost import XGBRegressor  # type: ignore

from music_flow.__init__ import __version__ as model_version
from music_flow.config import settings
from music_flow.core.features.preprocessing import feature_preprocessing
from music_flow.core.model_registry import ModelRegistry
from music_flow.core.utils import path_dataset, path_results
from music_flow.config import dataset_settings
from music_flow.model.training import Training
from music_flow.model.training_data import TrainingData

path_dataset_file = os.path.join(path_dataset, dataset_settings.FINAL_DATASET)
dataset = pd.read_csv(path_dataset_file, sep=";", index_col=0)  # type: ignore
dataset = feature_preprocessing(dataset)

# move to settings
# add datatype to settings
target_column = "plays"
columns_scope = [
    "number_of_available_markets",
    "num_artists",
    "duration_ms",
    "explicit",
    "popularity",
    "release_year",
    "release_month",
    "release_day",
    "date_is_complete",
    "danceability",
    "energy",
    "loudness",
    "mode",
    "speechiness",
    "acousticness",
    "instrumentalness",
    "liveness",
    "valence",
    "tempo",
    "time_signature",
    "A",
    "A#/Bb",
    "B",
    "C",
    "C#/Db",
    "D",
    "D#/Eb",
    "E",
    "F",
    "F#/Gb",
    "G",
    "G#/Ab",
    "Unknown",
]


X: pd.DataFrame = dataset[columns_scope]
y: pd.Series = dataset[target_column]

print(X.describe().T)
print(type(X))

dataset = TrainingData(X=X, y=y)
dataset.do_train_test_split()
data_log = dataset.get_data_log()
print(data_log)

estimator = XGBRegressor()

# Baseline - random values

folder_name = "Baseline0 - one value"

path_save = create_folder(os.path.join(path_model, folder_name))


 evaluator = Evaluator(
    y_test=self.y_test_reversed,
    y_pred=self.y_pred_reversed,
)
score_dict = evaluator.evaluate()
evaluator.visualize(path_save=path_save)


# Baseline 1 - simpel rule


# Baseline 2 - no-hyperparamter tuning