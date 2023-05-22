import logging
from contextlib import asynccontextmanager
from pathlib import Path
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from app.__init__ import __version__ as api_version
from app.config import settings
from app.response_messages import formating_failure, prediction_failure
from app.routers import song_form
from app.schemas import Features, Health, Prediction
from app.utils import map_score_to_emoji, prepare_raw_features_response
from music_flow import Predictor, get_features, get_raw_features
from music_flow.core.utils import path_app, path_results
from music_flow.config.core import model_settings

from music_flow.core.model_registry import ModelRegistry
from music_flow.config.core import settings as mf_settings

logger = logging.getLogger(__name__)


ml_model = {}
model_version = ""
model_folder = model_settings.MODEL_FOLDER


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the Machine Learning model

    Args:
        app (FastAPI): fastapi app object
    """
    predictor = Predictor(model_folder)
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

path_static = os.path.join(os.path.abspath(os.getcwd()), "app", "static")
logger.debug(f"static: {path_static}")

app.mount("/static", StaticFiles(directory=path_static), name="static")
app.include_router(song_form.router)


# @app.get("/download")
# async def download_model() -> dict:
#     """testing the model download"""
#     model_folder = model_settings.MODEL_FOLDER
#     logger.info(f"downloading model from s3 bucket: {model_folder}")
#     logger.info(f"(mf_settings.BUCKET_NAME: {mf_settings.BUCKET_NAME}")
#     logger.debug(path_results)
#     registry = ModelRegistry(mf_settings.BUCKET_NAME)
#     registry.download_folder(model_folder)
#     return {"message": "success"}


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
