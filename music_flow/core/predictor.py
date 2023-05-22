import logging
import os
import pickle
from typing import Optional

import pandas as pd

from music_flow.core.features.format_features import get_features
from music_flow.core.features.get_audio_features import get_raw_features
from music_flow.core.features.preprocessing import (
    feature_preprocessing,
    reverse_prediction,
)
from music_flow.core.model_finder import get_model_folder
from music_flow.core.utils import path_results, read_json
from music_flow.core.model_registry import ModelRegistry
from music_flow.config.core import settings, model_settings

logger = logging.getLogger(__name__)

# TODO: split up the classes in two file


class ModelLoader(object):
    def __init__(
        self,
        model_folder: Optional[str] = None,
        mode: str = "latest",
        metric: Optional[str] = None,
    ):
        if not model_folder:
            try:
                model_folder = get_model_folder(mode, metric)
            except Exception as e:
                print(e)
                model_folder = model_settings.MODEL_FOLDER

        logger.info(f"model_folder: {model_folder}")
        logger.debug(f"list of models: {os.listdir(path_results)}")

        if model_folder not in os.listdir(path_results):
            logger.info(f"downloading model from s3 bucket: {model_folder}")
            registry = ModelRegistry(settings.BUCKET_NAME)
            registry.download_folder(model_folder)

        self.model_folder = model_folder
        self.path_model_folder = os.path.join(path_results, model_folder)
        self.path_metadata = os.path.join(path_results, model_folder, "metadata.json")

    def load(self):
        # wrap into function
        self.load_metadata()
        self.features = self.metadata["data"]["features"]
        self.model_name = self.metadata["model"]["name"]
        self.path_model = os.path.join(self.path_model_folder, self.model_name)
        self.load_model()
        return self.metadata

    def load_model(self) -> None:
        """Load the model from the path_model path

        Raises:
            Exception: _description_
        """
        logger.info(f"loading model from {self.path_model}")
        try:
            with open(self.path_model, "rb") as handle:
                self.estimator = pickle.load(handle)
        except FileNotFoundError:
            raise Exception("Model not found!")
        logger.info("Model loaded")

        return

    def load_metadata(self) -> None:
        """Load the metadata of the model

        Returns:
            dict: _description_
        """
        try:
            self.metadata = read_json(self.path_metadata)
        except FileNotFoundError:
            raise Exception("metadata not found!")

    def get_features(self):
        return self.features

    def get_estimator(self):
        return self.estimator


class Predictor(object):
    def __init__(
        self,
        model_folder=None,
        mode="latest",
        metric=None,
        path=None,
    ):
        model_loader = ModelLoader(model_folder=model_folder, mode=mode, metric=metric)
        self.metadata = model_loader.load()
        self.features = model_loader.get_features()
        self.estimator = model_loader.get_estimator()
        self.model_version = self.get_model_version()

    def get_metdata(self):
        return self.metadata

    def get_features(self):
        return self.features

    def get_estimator(self):
        return self.estimator

    def get_model_version(self):
        model_info = self.metadata.get("model", {})
        model_version = model_info.get("model_version", None)
        return model_version

    def predict(self, song: str, artist: str, track_id: Optional[str] = None) -> dict:
        """
        Predict the number of streams for a given song

        Args:
            song (str): _description_
            artist (str): _description_
            track_id (Optional[str], optional): _description_. Defaults to None.

        Returns:
            dict: _description_
        """
        raw_features, _ = get_raw_features(song, artist)

        if raw_features["status"] != "success":
            keys = ["status", "failure_type", "description"]
            detail = {key: raw_features[key] for key in keys}
            raise Exception(detail)

        features = get_features(
            data=raw_features,
            track_name=song,
            artist_name=artist,
            flattened=True,
        )

        if not features:
            detail = {
                "status": "failure",
                "failure_type": "formatting",
                "description": "Could not format the features",
            }
            raise Exception(detail)

        prediction = self.predict_from_features(features)

        data_response = {
            "song": song,
            "artist": artist,
            "prediction": round(prediction, 2),
            "metadata": raw_features["metadata"],
        }
        return data_response

    def predict_from_features(self, features: dict) -> float:
        # TODO: remove pandas dependency
        sample = pd.DataFrame(features, index=[0])
        sample["plays"] = 0

        sample_formated = feature_preprocessing(sample)
        input_sample = sample_formated[self.features]

        scaled_prediction = self.estimator.predict(input_sample)
        prediction = reverse_prediction(scaled_prediction)
        return float(prediction[0])


if __name__ == "__main__":
    model_folder = "2023-01-21--12-33-25"
    predictor = Predictor(model_folder)
    song = "one more time"
    artist = "daft punk"
    data = predictor.predict(song=song, artist=artist)  # type: ignore
    print(data)
