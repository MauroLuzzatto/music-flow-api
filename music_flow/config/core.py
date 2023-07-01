import logging

from pydantic import BaseSettings

# add all the paths

# add csv names
# dataset.csv
# target_values.csv
# audio_features.csv


class ModelSettings(BaseSettings):
    MODEL_NAME: str = "model"
    MAX_PREDICTION_VALUE: int = 30
    MODEL_FOLDER: str = "2023-03-24--22-58-57"


class Settings(BaseSettings):
    NUMBER_OF_KAGGLE_DATASET_TRACKS: int = 32_000
    INCLUDE_AUDIO_ANALYSIS_DATASET: bool = False
    INCLUDE_AUDIO_ANALYSIS_API: bool = False
    API_MODE: bool = True
    # model registry s3 bucket name
    BUCKET_NAME: str = "musicflow-registry-398212703914"
    LOGGING_LEVEL = logging.DEBUG


model_settings = ModelSettings()
settings = Settings()
