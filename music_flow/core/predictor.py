import logging
from typing import Optional

import pandas as pd

from music_flow.core.features.format_features import get_features
from music_flow.core.features.get_audio_features import get_raw_features
from music_flow.core.features.preprocessing import (
    feature_preprocessing,
    reverse_prediction,
)
from music_flow.core.model_loader import ModelLoader

logger = logging.getLogger(__name__)


class Predictor(object):
    def __init__(
        self,
        model_folder=None,
        mode="latest",
        metric=None,
        path=None,
        path_registry=None,
    ):
        model_loader = ModelLoader(
            model_folder=model_folder,
            mode=mode,
            metric=metric,
            path_registry=path_registry,
        )
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
