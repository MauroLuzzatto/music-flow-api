import os
import pickle
from typing import Optional

import pandas as pd

from music_flow.core.get_playlist_tracks import get_playlist_tracks
from music_flow.core.spotify_api import SpotifyAPI
from music_flow.model.preprocessing import feature_preprocessing, reverse_prediction
from music_flow.prepare_data.features.create_audio_features_dataset import (
    format_features,
)
from music_flow.prepare_data.features.get_audio_features import get_features
from music_flow.utils import path_results

# def get_model_folder(mode="latest"):
#     list_folders = os.listdir(path_results)
#     if mode == "latest":
#         list_folders.sort()
#     return list_folders[0]


class Predictor(object):
    def __init__(self, model_folder):
        path_results_model = os.path.join(path_results, model_folder)
        self.path_model = os.path.join(path_results_model, "XGBRegressor.pickle")
        self.load_model()

    def load_model(self):
        with open(self.path_model, "rb") as handle:
            self.estimator = pickle.load(handle)
        print("Model loaded")

    def load_model_metadata(self):
        pass

    def make_prediction(
        self, song: str, artist: str, track_id: Optional[str] = None
    ) -> dict:

        data, status_code = get_features(song, artist, track_id)
        status = data["status"]

        if data["status"] != "success":
            data_response = {
                "error": {"code": status_code, "message": data["failure_type"]}
            }
            return data_response

        features = format_features(data=data, track_name=song, artist_name=artist)
        sample = pd.DataFrame(features, index=[0])
        sample["plays"] = 0

        sample_formated, columns_scope = feature_preprocessing(sample)
        input_sample = sample_formated[columns_scope]

        scaled_prediction = self.estimator.predict(input_sample)
        prediction = reverse_prediction(scaled_prediction)

        data_response = {
            "song": song,
            "artist": artist,
            "prediction": round(float(prediction[0]), 2),
            "metadata": data["metadata"],
            "status": status,
        }
        return data_response


if __name__ == "__main__":

    model_folder = "2023-01-21--12-33-25"

    user_id = "1157239771"
    playlist_id = "37i9dQZEVXcJlIMuDHGHCM"

    spotifAPI = SpotifyAPI()
    paylist, status_code = spotifAPI.get_playlist_items(playlist_id=playlist_id)
    tracks = get_playlist_tracks(paylist)

    predictor = Predictor(model_folder)

    predictions = []
    for track in tracks[:4]:

        song = track["track_name"]
        artist = track["artists"]
        track_id = track["track_id"]
        print(song, artist, track_id)

        data = predictor.make_prediction(song=song, artist=artist, track_id=track_id)
        print(data)
