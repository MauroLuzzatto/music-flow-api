import os
from typing import List

import numpy as np
import pandas as pd
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse

from track_recommender.core.get_playlist_tracks import get_playlist_tracks
from track_recommender.core.playlist_handler import PlaylistHandler
from track_recommender.core.predictor import Predictor
from track_recommender.utils import dotenv_path

load_dotenv(dotenv_path)


user_id = "1157239771"
playlist_id_discover_weekly = "37i9dQZEVXcJlIMuDHGHCM"

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8000/callback/"


model_folder = "2023-01-21--12-33-25"


app = FastAPI()


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
    auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=playlist-modify-private playlist-modify-public"
    return HTMLResponse(content=f'<a href="{auth_url}">Authorize</a>')


@app.get("/callback")
def callback(code):

    auth_headers = get_access_token(code)
    playlist = PlaylistHandler(auth_headers)

    playlist_items, status_code = playlist.get_playlist_items(
        playlist_id=playlist_id_discover_weekly
    )
    tracks = get_playlist_tracks(playlist_items)

    predictor = Predictor(model_folder)

    predictions = []
    for track in tracks:

        song = track["track_name"]
        artist = track["artists"]
        track_id = track["track_id"]

        prediction = predictor.make_prediction(
            song=song,
            artist=artist,
            track_id=track_id,
        )
        entry = {
            "song": song,
            "artist": artist,
            "track_id": track_id,
            "prediction": prediction[0],
        }

        print(entry)
        predictions.append(entry)

    predictions.sort(key=lambda row: row["prediction"], reverse=True)
    print(predictions)

    name = "Discover Weekly - autosort"
    description = "Your sorted Discover weekly music, enjoy!"

    params = {
        "name": name,
        "description": description,
        "public": True,
    }

    response, status_code = playlist.create_playlist(user_id, params)
    new_playlist_id = response["id"]
    track_ids = [track["track_id"] for track in predictions]
    response, status_code = playlist.add_tracks_to_playlist(
        playlist_id=new_playlist_id, track_ids=track_ids
    )

    if status_code == 201:
        return {"message": "Track added successfully!"}
    else:
        return {"error": response.json()}


if __name__ == "__main__":
    uvicorn.run(app, debug=True)
