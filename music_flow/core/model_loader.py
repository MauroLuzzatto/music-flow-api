import logging
import os
import pickle
from typing import Optional

from music_flow.config.core import model_settings, settings
from music_flow.core.model_finder import get_model_folder
from music_flow.core.model_registry import ModelRegistry
from music_flow.core.utils import path_results, read_json

logger = logging.getLogger(__name__)


class ModelLoader(object):
    def __init__(
        self,
        model_folder: Optional[str] = None,
        mode: str = "latest",
        metric: Optional[str] = None,
        path_registry: Optional[str] = None,
    ):
        if not model_folder:
            try:
                model_folder = get_model_folder(mode, metric)
            except Exception as e:
                logger.error(e)
                model_folder = model_settings.MODEL_FOLDER

        self.model_folder = model_folder
        logger.info(f"model_folder: {self.model_folder}")

        if not path_registry:
            self.path_registry = path_results
        else:
            self.path_registry = path_registry

        try:
            list_of_models = os.listdir(self.path_registry)
        except FileNotFoundError:
            list_of_models = []

        logger.debug(f"list of models: {list_of_models}")

        if model_folder not in list_of_models:
            logger.info(f"downloading model from s3 bucket: {model_folder}")
            registry = ModelRegistry(
                settings.BUCKET_NAME, path_registry=self.path_registry
            )
            registry.download_folder(model_folder)

        self.path_model_folder = os.path.join(self.path_registry, model_folder)
        self.path_metadata = os.path.join(self.path_model_folder, "metadata.json")

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
