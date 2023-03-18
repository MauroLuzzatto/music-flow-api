import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from mangum import Mangum

# from app.__init__ import __version__ as api_version
# from app.config import settings, setup_app_logging
# from app.schemas import Features, Health, Prediction, RawFeatures
# from app.utils import map_score_to_emoji, prepare_raw_features_response
from music_flow import Predictor, get_features, get_raw_features

# # setup logging as early as possible
# # setup_app_logging(config=settings)

logger = logging.getLogger(__name__)

model_version = "0.1.0"

ml_model = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load the Machine Learning model

    Args:
        app (FastAPI): _description_
    """
    predictor = Predictor(model_version)
    model_metadata = predictor.get_metdata()
    ml_model["predict"] = predictor.predict_from_features
    ml_model["metadata"] = model_metadata
    yield

    # Clean up the ML models and release the resources
    ml_model.clear()


# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     description=settings.DESCRIPTION,
#     version=api_version,
#     lifespan=lifespan,  # type: ignore
# )

app = FastAPI(
    lifespan=lifespan,  # type: ignore
)

# from pathlib import Path
# from fastapi.staticfiles import StaticFiles
# from app.routers import lyrics
# base_path = Path("/home/maurol/track-recommender/app").absolute()
# app.mount("/static", StaticFiles(directory=str(base_path / "static")), name="static")
# app.include_router(lyrics.router)


def prepare_raw_features_response(raw_features, status_code):
    keys = ["status", "failure_type", "description"]
    detail = {key: raw_features[key] for key in keys}
    detail["status_code"] = status_code
    return detail


def map_score_to_emoji(score):
    values = [
        (0.3, "😐", "This song needs to grow on me!"),
        (0.5, "🙂", "Nice track!"),
        (1.0, "😃", "Cool track!"),
        (2.0, "😄", "OMG, how did I not know this song?"),
        (100.0, "😍", "What a banger!"),
    ]
    emoji = ""
    text = ""
    for threshold, emoji, text in values:
        if score < threshold:
            break

    return {"emoji": emoji, "text": text}


@app.get("/")
async def root() -> dict:
    message = (
        "Welcome to the music flow API! "
        "Here is an example: musicflow.link/prediction/?song=sun&artist=caribou"
    )
    return {"message": message}


# @app.get("/health")
# async def health() -> Health:
#     """Get the health of the API"""
#     health = Health(
#         name=settings.PROJECT_NAME,
#         description=settings.DESCRIPTION,
#         api_version=api_version,
#         model_version=model_version,
#     )
#     return health


@app.get("/prediction/")
async def get_prediction_api(song: str, artist: str):
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
            "failure_type": "formatting",
            "description": "Could not format the features",
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
            "failure_type": "prediction",
            "description": "Failed to make a prediction",
            "status_code": status_code,
        }
        raise HTTPException(status_code=status_code, detail=detail)

    user_message = map_score_to_emoji(prediction)
    description = (
        "The predicted number of future streams of the song based on the Spotify API"
        " audio features."
    )

    data_response = {
        "song": song,
        "artist": artist,
        "prediction": round(prediction, 2),
        "description": description,
        "song_metadata": raw_features["metadata"],
        "message": user_message,
    }
    # return Prediction(**data_response)
    return data_response


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
        RawFeatures: raw features object
    """
    raw_features, status_code = get_raw_features(song, artist)

    if raw_features["status"] != "success":
        detail = prepare_raw_features_response(raw_features, status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    return raw_features


@app.get("/features/")
async def get_features_api(song: str, artist: str) -> dict:
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
            "failure_type": "formatting",
            "description": "Could not format the features",
            "status_code": status_code,
        }
        raise HTTPException(status_code=status_code, detail=detail)

    # return Features(**features)
    return features


handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
