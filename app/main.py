import uvicorn
from fastapi import FastAPI

from app.utils import map_score_to_emoji
from track_recommender import Predictor, SpotifyAPI, format_features, get_features

model_folder = "2023-01-21--12-33-25"

spotify_api = SpotifyAPI()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/prediction/")
def get_prediction(song: str, artist: str):

    predictor = Predictor(model_folder)
    data = predictor.make_prediction(song=song, artist=artist)
    if "error" in data:
        return data

    user_message = map_score_to_emoji(data["prediction"])
    data.update(user_message)
    return data


@app.get("/raw_features/")
async def get_raw_features(song: str, artist: str):
    data, status_code = get_features(song, artist)

    if data["status"] != "success":
        data_response = {
            "error": {"code": status_code, "message": data["failure_type"]}
        }
        return data_response
    return data


@app.get("/features/")
async def read_item(song: str, artist: str):
    data, status_code = get_features(song, artist)

    if data["status"] != "success":
        data_response = {
            "error": {"code": status_code, "message": data["failure_type"]}
        }
        return data_response

    audio_features = format_features(data=data, track_name=song, artist_name=artist)
    return audio_features


if __name__ == "__main__":
    uvicorn.run(app="app.main:app", reload=True)
