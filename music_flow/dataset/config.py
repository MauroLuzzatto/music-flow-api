from pydantic_settings import BaseSettings


class DatasetSettings(BaseSettings):
    RAW_STREAMS: str = "streams.csv"
    TARGERT_VALUES: str = "target_values.csv"
    KAGGEL_DATASET: str = "kaggle_tracks.csv"
    AUDIO_FEATURES: str = "audio_features.csv"
    FINAL_DATASET: str = "dataset.csv"


dataset_settings = DatasetSettings()
