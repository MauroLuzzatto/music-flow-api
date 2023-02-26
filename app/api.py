import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel

from app.schemas import Features, Health, Prediction, RawFeatures
from music_flow import Predictor, SpotifyAPI, format_features, get_features
from music_flow.core.utils import map_score_to_emoji

spotify_api = SpotifyAPI()


# class Song(BaseModel):
#     song: str


# class Artist(BaseModel):
#     artist: str


# class SongArtist(BaseModel):
#     song: str
#     artist: str


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to the music flow API!"}


@app.get("/health", response_model=Health, status_code=200)
def health() -> dict:
    """
    Root Get
    """
    health = Health(
        name=settings.PROJECT_NAME, api_version=__version__, model_version=model_version
    )

    return health.dict()


@app.get("/prediction/")
def get_prediction(song: str, artist: str):
    """_summary_

    Args:
        song (str): _description_
        artist (str): _description_

    Raises:
        HTTPException: _description_

    Returns:
        Prediction: _description_
    """

    predictor = Predictor()
    data = predictor.make_prediction(song=song, artist=artist)
    if "error" in data:
        raise HTTPException(
            status_code=404,
            detail=f"failure_type: {data['error']['failure_type']}",
        )

    user_message = map_score_to_emoji(data["prediction"])
    data["message"] = user_message
    # return Prediction(**data)
    return JSONResponse(content=data)


@app.get("/raw_features/")
async def get_raw_features(song: str, artist: str):
    """_summary_

    Args:
        song (str): _description_
        artist (str): _description_

    Raises:
        HTTPException: _description_

    Returns:
        _type_: _description_
    """

    features, _ = get_features(song, artist)

    if features["status"] != "success":
        raise HTTPException(
            status_code=404,
            detail=f"failure_type: {features['failure_type']}",
        )
    return JSONResponse(content=features)


@app.get("/features/")
async def get_features_api(song: str, artist: str):

    features, _ = get_features(song, artist)

    if features["status"] != "success":
        raise HTTPException(
            status_code=404,
            detail=f"failure_type: {features['failure_type']}",
        )

    formatted_features = format_features(
        data=features, track_name=song, artist_name=artist
    )
    return JSONResponse(content=formatted_features)


# handler = Mangum(app)


if __name__ == "__main__":
    uvicorn.run(app="serve_app.main:app", reload=True)
