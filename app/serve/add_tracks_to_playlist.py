import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from music_flow.core.get_playlist_tracks import get_playlist_tracks
from music_flow.core.playlist_handler import PlaylistHandler
from music_flow.core.predictor import Predictor
from music_flow.core.utils import path_env

load_dotenv(path_env)


user_id = "1157239771"
playlist_id_discover_weekly = "37i9dQZEVXcJlIMuDHGHCM"

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8000/callback/"


model_folder = "2023-02-01--22-06-44"


app = FastAPI()

# Global variable to store the auth token
AUTH_TOKEN = ""


def get_access_token(auth_code: str):
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": redirect_uri,
        },
        auth=(client_id, client_secret),  # type: ignore
    )
    access_token = response.json()["access_token"]
    return {"Authorization": "Bearer " + access_token}


@app.get("/")
def auth():
    scope = ["playlist-modify-private", "playlist-modify-public"]
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={' '.join(scope)}"
    )
    return HTMLResponse(content=f'<a href="{auth_url}">Authorize</a>')


@app.get("/callback")
def callback(code):
    global AUTH_TOKEN
    AUTH_TOKEN = get_access_token(code)
    return {"message": "Successfully logged in"}


@app.get("/update_playlist")
def update_playlist():
    playlist_handler = PlaylistHandler(headers=AUTH_TOKEN)

    playlist_items, status_code = playlist_handler.get_playlist_items(
        playlist_id=playlist_id_discover_weekly
    )
    tracks = get_playlist_tracks(playlist_items)

    predictor = Predictor(model_folder)

    predictions = []
    for track in tracks:
        prediction = predictor.make_prediction(
            song=track["track_name"],
            artist=track["artists"],
            track_id=track["track_id"],
        )
        prediction["track_id"] = track["track_id"]
        print(prediction)
        predictions.append(prediction)

    predictions.sort(key=lambda row: row["prediction"], reverse=True)
    print(predictions)

    playlist_name = "Discover Weekly"
    name = f"{playlist_name} - autosort"
    description = f"Your sorted {playlist_name} music, enjoy!"

    params = {
        "name": name,
        "description": description,
        "public": True,
    }

    response, status_code = playlist_handler.create_playlist(user_id, params)
    new_playlist_id = response["id"]
    track_ids = [track["track_id"] for track in predictions]

    response, status_code = playlist_handler.add_tracks_to_playlist(
        playlist_id=new_playlist_id, track_ids=track_ids
    )

    if status_code == 201:
        return {"message": "Track added successfully!"}
    else:
        return {"error": response.json()}


if __name__ == "__main__":
    uvicorn.run(app, debug=True)
