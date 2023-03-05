import os
import pickle
from typing import Optional

import pandas as pd

from music_flow.core.features.format_features import format_features
from music_flow.core.features.get_audio_features import get_features
from music_flow.core.features.preprocessing import (
    feature_preprocessing,
    reverse_prediction,
)
from music_flow.core.get_playlist_tracks import get_playlist_tracks
from music_flow.core.model_finder import get_model_folder
from music_flow.core.spotify_api import SpotifyAPI
from music_flow.core.utils import path_results, read_json

description = "The number of predicted future streams of the song"


class Predictor(object):
    def __init__(
        self, model_version, model_folder=None, mode="latest", metric=None, path=None
    ):
        if not model_folder:
            model_folder = get_model_folder(mode, metric, path)

        # TODO: allow model to be loaded from .env file

        self.path_model_folder = os.path.join(path_results, model_folder)
        self.path_metadata = os.path.join(self.path_model_folder, "metadata.json")

        self.load_metadata()
        self.features = self.metadata["data"]["features"]
        self.model_name = self.metadata["model"]["name"]
        self.path_model = os.path.join(self.path_model_folder, self.model_name)
        self.load_model()

    def load_model(self) -> None:
        """
        Load the model from the path_model

        Raises:
            Exception: _description_
        """
        print(f"loading model from {self.path_model}")
        try:
            with open(self.path_model, "rb") as handle:
                self.estimator = pickle.load(handle)
        except FileNotFoundError:
            raise Exception("Model not found!")
        print("Model loaded")

    def load_metadata(self) -> None:
        """_summary_

        Returns:
            dict: _description_
        """
        try:
            self.metadata = read_json(self.path_metadata)
        except FileNotFoundError:
            raise Exception("metadata not found!")

    def get_metdata(self):
        return self.metadata

    def make_prediction(
        self,
        song: str,
        artist: str,
        track_id: Optional[str] = None,
    ) -> dict:
        data, status_code = get_features(song, artist, track_id)
        status = data["status"]

        if data["status"] != "success":
            data_response = {
                "error": {"code": status_code, "failure_type": data["failure_type"]}
            }
            return data_response

        features = format_features(data=data, track_name=song, artist_name=artist)

        # TODO: remove pandas dependency
        sample = pd.DataFrame(features, index=[0])
        sample["plays"] = 0

        sample_formated = feature_preprocessing(sample)
        input_sample = sample_formated[self.features]

        scaled_prediction = self.estimator.predict(input_sample)
        prediction = reverse_prediction(scaled_prediction)

        data_response = {
            "song": song,
            "artist": artist,
            "prediction": round(float(prediction[0]), 2),
            "description": description,
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
