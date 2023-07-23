import logging

from pydantic import BaseSettings
import os


class PathSettings(BaseSettings):
    path: str = os.getcwd()
    path_base: str = os.path.join(path, "music_flow")
    path_env: str = os.path.join(path, ".env")
    path_app: str = os.path.join(path, "app")
    path_results: str = os.path.join(path, "results")
    path_registry: str = os.path.join(path, "registry")
    path_reports: str = os.path.join(path, "reports")
    path_data_lake: str = os.path.join(path, "data_lake")
    path_data_lake_success: str = os.path.join(path_data_lake, "success")
    path_data_lake_failed: str = os.path.join(path_data_lake, "failed")
    path_data: str = os.path.join(path, "data")
    path_features: str = os.path.join(path_data, "features")
    path_dataset: str = os.path.join(path_data, "dataset")
    path_raw: str = os.path.join(path_data, "raw")


class DatasetSettings(BaseSettings):
    RAW_STREAMS: str = "streams.csv"
    TARGERT_VALUES: str = "target_values.csv"
    KAGGEL_DATASET: str = "kaggle_tracks.csv"
    AUDIO_FEATURES: str = "audio_features.csv"
    FINAL_DATASET: str = "dataset.csv"

    test_size: float = 0.2
    random_state: int = 42


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


class FeatureSettings(BaseSettings):
    # TODO: add datatype of each feature
    target_column: str = "plays"
    columns_scope: list[str] = [
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


settings = Settings()
model_settings = ModelSettings()
dataset_settings = DatasetSettings()
path_settings = PathSettings()
