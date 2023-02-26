"""Top-level package for track_recommender."""

__author__ = """Mauro Luzzatto"""
__email__ = "mauroluzzatto@hotmail.com"

import os

from music_flow.core.predictor import Predictor
from music_flow.core.spotify_api import SpotifyAPI
from music_flow.core.utils import path_base
from music_flow.features.format_features import format_features
from music_flow.features.get_audio_features import get_features

__all__ = [Predictor, SpotifyAPI, format_features, get_features]


with open(os.path.join(path_base, "VERSION")) as version_file:
    __version__ = version_file.read().strip()
