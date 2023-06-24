import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from app.__init__ import __version__ as api_version
from app.config import settings
from app.utils.response_messages import formating_failure, prediction_failure
from app.utils.get_registry_path import setup

from app.schemas import Prediction
from app.utils.response_formatter import (
    map_score_to_emoji,
)
from music_flow.config.core import model_settings
from music_flow.core.utils import path_app
from music_flow import Predictor, get_formatted_features

from app.routers import api, root

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

ml_model = {}
model_folder = model_settings.MODEL_FOLDER
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
    openapi_url="/api",
    docs_url="/docs",
    root_path=settings.ROOT_PATH,
    servers=[{"url": settings.ROOT_PATH}],
)

app.include_router(api.router)
app.include_router(root.router)


base_path = Path(path_app).absolute()
path_static = str(base_path / "static")
logger.debug(f"Base path: {base_path}")
logger.debug(f"static: {path_static}")

app.mount("/static", StaticFiles(directory=path_static), name="static")


@app.get("/api/prediction/", tags=["API"])
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

    raw_features = await api.get_raw_features_api(song, artist)
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
            "description": f"{prediction_failure.description}: error {e}",
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
