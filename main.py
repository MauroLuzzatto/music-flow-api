import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from mangum import Mangum

from app.__init__ import __version__ as api_version
from app.config import settings
from app.failures import formating_failure, prediction_failure
from app.schemas import Features, Health, Prediction
from app.utils import map_score_to_emoji, prepare_raw_features_response
from music_flow import Predictor, get_features, get_raw_features

logger = logging.getLogger(__name__)

model_version = "0.1.0"

ml_model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the Machine Learning model

    Args:
        app (FastAPI): fastapi app object
    """
    predictor = Predictor(model_version)
    model_metadata = predictor.get_metdata()
    ml_model["predict"] = predictor.predict_from_features
    ml_model["metadata"] = model_metadata
    yield

    # Clean up the ML models and release the resources
    ml_model.clear()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.API_DESCRIPTION,
    version=api_version,
    lifespan=lifespan,  # type: ignore
)


# from pathlib import Path
# from fastapi.staticfiles import StaticFiles
# from app.routers import lyrics
# from music_flow.core.utils import path_app
# base_path = Path(path_app).absolute()
# app.mount("/static", StaticFiles(directory=str(base_path / "static")), name="static")
# app.include_router(lyrics.router)


@app.get("/")
async def root() -> dict:
    """Get the root of the API"""
    return {"message": settings.MESSAGE}


@app.get("/health")
async def health_api() -> Health:
    """Get the health of the API"""
    health = Health(
        name=settings.PROJECT_NAME,
        description=settings.API_DESCRIPTION,
        api_version=api_version,
        model_version=model_version,
    )
    return health


@app.get("/prediction/")
async def get_prediction_api(song: str, artist: str) -> Prediction:
    """Get the model predictions

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song or audio features could not be found or fetched from Spotify API
                or if formatting of the features failed
                or if the prediction failed

    Returns:
        Prediction: prediction object
    """

    raw_features, status_code = get_raw_features(song, artist)
    if raw_features["status"] != "success":
        detail = prepare_raw_features_response(raw_features, status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    features = get_features(
        data=raw_features,
        track_name=song,
        artist_name=artist,
        flattened=True,
    )

    if not features:
        status_code = 500
        detail = {
            "status": "failure",
            "failure_type": formating_failure.failure_type,
            "description": formating_failure.description,
            "status_code": status_code,
        }
        raise HTTPException(status_code=status_code, detail=detail)

    try:
        prediction = ml_model["predict"](features)
    except Exception as e:
        logging.debug(e)
        status_code = 500
        detail = {
            "status": "failure",
            "failure_type": prediction_failure.failure_type,
            "description": prediction_failure.description,
            "status_code": status_code,
        }
        raise HTTPException(status_code=status_code, detail=detail)

    user_message = map_score_to_emoji(prediction)

    data_response = {
        "song": song,
        "artist": artist,
        "prediction": round(prediction, 2),
        "description": settings.PREDICTION_DESCRIPTION,
        "song_metadata": raw_features["metadata"],
        "message": user_message,
    }
    return Prediction(**data_response)


@app.get("/raw_features/")
async def get_raw_features_api(song: str, artist: str) -> dict:
    """
    Get the raw audio features of a song from the Spotify API

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song or audio features could not be found or fetched from Spotify API

    Returns:
        dict: dict with raw features
    """
    raw_features, status_code = get_raw_features(song, artist)

    if raw_features["status"] != "success":
        detail = prepare_raw_features_response(raw_features, status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    return raw_features


@app.get("/features/")
async def get_features_api(song: str, artist: str) -> Features:
    """
    Get the preprocessed audio features that are used for making predictions

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song or audio features could not be found or fetched from Spotify API
            or if formatting of the features failed

    Returns:
        Features: features object
    """
    raw_features, status_code = get_raw_features(song, artist)

    if raw_features["status"] != "success":
        detail = prepare_raw_features_response(raw_features, status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    features = get_features(
        data=raw_features,
        track_name=song,
        artist_name=artist,
        flattened=False,
    )

    if not features:
        status_code = 500
        detail = {
            "status": "failure",
            "failure_type": formating_failure.failure_type,
            "description": formating_failure.description,
            "status_code": status_code,
        }
        raise HTTPException(status_code=status_code, detail=detail)

    return Features(**features)


handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
