from pydantic import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MusicFlow API"
    API_DESCRIPTION: str = (
        "This API predicts the number of song streams on Spotify based on"
        " a personal streaming history. The API is part of the MusicFlow project, where"
        " the history on Spotify is used to create a dataset and then train a machine learning"
        " model. The prediction is done using the Spotify audio features and track metadata."
    )

    MESSAGE: str = (
        "Welcome to the music flow API! "
        "Here is an example: "
        "https://musicflow.link/prediction/?song=sun&artist=caribou"
    )

    PREDICTION_DESCRIPTION = str(
        "The predicted number of future streams of the song based on the Spotify API"
        " audio features."
    )

    class Config:
        case_sensitive = True


settings = Settings()
