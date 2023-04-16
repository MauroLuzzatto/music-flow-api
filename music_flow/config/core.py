from pydantic import BaseSettings

# add all the paths

# add csv names
# dataset.csv
# target_values.csv
# audio_features.csv


class ModelSettings(BaseSettings):
    MODEL_NAME: str = "model"
    MAX_PREDICTION_VALUE: int = 30


class Settings(BaseSettings):
    NUMBER_OF_KAGGLE_DATASET_TRACKS: int = 32_000
    INCLUDE_AUDIO_ANALYSIS_DATASET: bool = False
    INCLUDE_AUDIO_ANALYSIS_API: bool = True
    API_MODE: bool = True


model_settings = ModelSettings()
settings = Settings()