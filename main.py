import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from mangum import Mangum

from app.__init__ import __version__ as api_version
from app.config import settings
from app.core.analytics import Analytics
from app.core.aws import upload_json_to_s3
from app.routers import api, root
from app.schemas import Prediction
from app.utils.get_registry_path import setup
from app.utils.response_formatter import map_score_to_emoji
from app.utils.response_messages import get_exception_details
from app.utils.runtime import get_is_lambda_runtime
from music_flow import Predictor, get_formatted_features
from music_flow.config import model_settings
from music_flow.core.utils import path_app

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

ml_model = {}
model_folder = model_settings.MODEL_FOLDER

is_testing = False
is_lambda_runtime = get_is_lambda_runtime()
path_registry = setup(is_lambda_runtime)


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

app.scores = []

path_static = str(Path(path_app).absolute() / "static")
app.mount("/static", StaticFiles(directory=path_static), name="static")

app.add_middleware(
    Analytics, is_lambda_runtime=is_lambda_runtime, is_testing=is_testing
)
app.include_router(api.router)
app.include_router(root.router)


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
    logger.debug(f"features: {features}")

    if not features:
        status_code = 500
        detail = get_exception_details("formating_failure", status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    metadata = features.get("metadata")
    logger.debug(f"metadata: {metadata}")
    del features["metadata"]

    try:
        prediction = ml_model["predict"](features)
        logger.debug(f"prediction: {prediction}")
    except Exception as e:
        logging.debug(e)
        status_code = 500
        detail = get_exception_details("prediction_failure", status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    user_message = map_score_to_emoji(prediction)

    data_response = {
        "song": song,
        "artist": artist,
        "prediction": round(prediction, 2),
        "song_metadata": metadata,
        "description": settings.PREDICTION_DESCRIPTION,
        "message": user_message,
        "preview_url": raw_features["track"]["preview_url"],
        "features": features,
    }

    if is_lambda_runtime or is_testing:
        save_folder = (
            settings.FOLDER_PREDICTIONS if not is_testing else "predictions_test"
        )
        name = str(uuid.uuid4())
        upload_json_to_s3(
            data_dict=data_response,
            save_name=f"{save_folder}/{name}.json",
        )

    return Prediction(**data_response)


handler = Mangum(app)

if __name__ == "__main__":
    logger.warning("Running in development mode. Do not run like this in production.")
    uvicorn.run(app="main:app", reload=True)
