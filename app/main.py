import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.__init__ import __version__ as api_version
from app.config import Settings
from app.schemas import Features, Health, Prediction, RawFeatures
from music_flow import Predictor, format_features, get_features
from music_flow.core.utils import map_score_to_emoji

settings = Settings()

model_version = "0.1.0"
predictor = Predictor(model_version)
model_metadata = predictor.load_model_metadata()
print(model_metadata)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=api_version,
)


@app.get("/")
async def root():
    return {"message": "Welcome to the music flow API!"}


@app.get("/health", response_model=Health)
async def health() -> dict:
    """Get the health of the API"""
    health = Health(
        name=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        api_version=api_version,
        model_version=model_version,
    )
    return health.dict()


@app.get("/prediction/")
async def get_prediction(song: str, artist: str) -> Prediction:
    """Get the model predictions

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song could not be found or the prediction failed

    Returns:
        Prediction: prediction object
    """
    data = predictor.make_prediction(song=song, artist=artist)

    if "error" in data:
        raise HTTPException(
            status_code=404,
            detail=f"failure_type: {data['error']['failure_type']}",
        )

    user_message = map_score_to_emoji(data["prediction"])
    data["message"] = user_message
    return Prediction(**data)


@app.get("/raw_features/")
async def get_raw_features(song: str, artist: str) -> RawFeatures:
    """_summary_

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song could not be found or the prediction failed

    Returns:
        RawFeatures: raw features object
    """

    features, _ = get_features(song, artist)

    if features["status"] != "success":
        raise HTTPException(
            status_code=404,
            detail=f"failure_type: {features['failure_type']}",
        )
    return RawFeatures(**features)


@app.get("/features/")
async def get_features_api(song: str, artist: str):
    """
    Get the audio features of a song

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song could not be found or the prediction failed

    Returns:
        Features: features object
    """

    features, _ = get_features(song, artist)

    if features["status"] != "success":
        raise HTTPException(
            status_code=404,
            detail=f"failure_type: {features['failure_type']}",
        )

    formatted_features = format_features(
        data=features,
        track_name=song,
        artist_name=artist,
        flattened=False,
    )
    # return
    return formatted_features


# handler = Mangum(app)


if __name__ == "__main__":
    uvicorn.run(app="app.main:app", reload=True)
