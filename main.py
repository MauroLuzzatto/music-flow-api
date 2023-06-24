import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from app.__init__ import __version__ as api_version
from app.config import settings
from app.utils.response_messages import formating_failure, prediction_failure
from app.routers import song_form
from app.schemas import Features, Health, Prediction
from app.utils.response_formatter import (
    map_score_to_emoji,
    prepare_raw_features_response,
)
from music_flow import Predictor, get_formatted_features, get_raw_features
from music_flow.config.core import model_settings
from music_flow.core.utils import path_app

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

ml_model = {}
model_version = ""
model_folder = model_settings.MODEL_FOLDER


def setup() -> Optional[str]:
    """_summary_

    Returns:
        Optional[str]: _description_
    """

    AWS_EXECUTION_ENV = os.environ.get("AWS_EXECUTION_ENV")
    is_lambda_runtime = bool(AWS_EXECUTION_ENV)

    if is_lambda_runtime:
        # lambda can only write to the "/tmp" folder, if we want to download
        # the model from s3 bucket we need to set the path to "/tmp"
        path_registry = "/tmp"
    else:
        path_registry = None

    logger.info(f"AWS_EXECUTION_ENV: {AWS_EXECUTION_ENV}")
    logger.debug(f"is_lambda_runtime: {is_lambda_runtime}")
    logger.debug(f"path_registry: {path_registry}")
    return path_registry


path_registry = setup()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the Machine Learning model

    Args:
        app (FastAPI): fastapi app object
    """
    predictor = Predictor(
        model_folder=model_folder,
        path_registry=path_registry,
    )
    model_metadata = predictor.get_metdata()

    ml_model["predict"] = predictor.predict_from_features
    ml_model["metadata"] = model_metadata

    global model_version
    model_version = predictor.get_model_version()

    yield

    # Clean up the ML models and release the resources
    ml_model.clear()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.API_DESCRIPTION,
    version=api_version,
    lifespan=lifespan,  # type: ignore
    # openapi_prefix="/Prod"
)


base_path = Path(path_app).absolute()
logger.debug(f"Base path: {base_path}")
logger.debug(f"static: {str(base_path / 'static')}")

path_static = os.path.join(path_app, "static")
logger.debug(f"static_v2: {path_static}")

app.mount("/static", StaticFiles(directory=path_static), name="static")
app.include_router(song_form.router)


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
        project_url=settings.GITHUB_URL,
    )
    return health


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
    raw_features = await get_raw_features_api(song, artist)
    features = get_formatted_features(data=raw_features, is_flattened=False)
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

    raw_features = await get_raw_features_api(song, artist)
    features = get_formatted_features(data=raw_features, is_flattened=True)

    if not features:
        status_code = 500
        detail = {
            "status": "failure",
            "failure_type": formating_failure.failure_type,
            "description": formating_failure.description,
            "status_code": status_code,
        }
        raise HTTPException(status_code=status_code, detail=detail)

    metadata = features["metadata"]
    logger.debug(metadata)
    del features["metadata"]
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
        "song_metadata": metadata,
        "message": user_message,
        "preview_url": raw_features["track"]["preview_url"],
    }
    return Prediction(**data_response)


handler = Mangum(app)

if __name__ == "__main__":
    logger.warning("Running in development mode. Do not run like this in production.")
    uvicorn.run(app="main:app", reload=True)
