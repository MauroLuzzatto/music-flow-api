"""Top-level package for track_recommender."""

__author__ = """Mauro Luzzatto"""
__email__ = "mauroluzzatto@hotmail.com"

import os

from music_flow.core import Predictor, SpotifyAPI, get_features, get_raw_features
from music_flow.core.utils import path_base

__all__ = [Predictor, SpotifyAPI, get_features, get_raw_features]


with open(os.path.join(path_base, "VERSION")) as version_file:
    __version__ = version_file.read().strip()
