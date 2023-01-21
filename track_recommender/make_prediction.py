import os
import pickle
import sys
import time
from pprint import pprint

import numpy as np
import pandas as pd

print(sys.path)


from dotenv import load_dotenv

from track_recommender.core.spotify_api import SpotifyAPI
from track_recommender.model.preprocessing import (
    feature_preprocessing,
    reverse_prediction,
)
from track_recommender.prepare_data.features.create_audio_features_dataset import (
    format_features,
)
from track_recommender.prepare_data.features.get_audio_features import get_features
from track_recommender.prepare_data.get_playlist_tracks import get_playlist_tracks

dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)
load_dotenv(dotenv_path)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

model_folder = "2023-01-21--12-33-25"

path_results = f"/home/maurol/track-recommender/results/{model_folder}"
path_model = os.path.join(path_results, "XGBRegressor.pickle")

with open(path_model, "rb") as handle:
    estimator = pickle.load(handle)

song = "Home"
artist = "Caribou"


# song = "Never Fight A Man With A Perm"
# artist = "IDLES"

# song = "Penawar Duka"
# artist = "Reeka"


def make_prediction(song, artist, track_id=None):

    features = get_features(song, artist, track_id)
    formated_features = format_features(
        data=features, track_name=song, artist_name=artist
    )
    sample = pd.DataFrame(formated_features, index=[0])
    sample["plays"] = 0

    sample_formated, columns_scope = feature_preprocessing(sample)
    input_sample = sample_formated[columns_scope]

    scaled_prediction = estimator.predict(input_sample)
    prediction = reverse_prediction(scaled_prediction)
    return prediction


playlist_id = "37i9dQZEVXcJlIMuDHGHCM"

spotifAPI = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
paylist, status_code = spotifAPI.get_playlist_items(playlist_id=playlist_id)
tracks = get_playlist_tracks(paylist)

predictions = []
for track in tracks[:]:
    print(track)

    song = track["track_name"]
    artist = track["artists"]
    track_id = track["track_id"]

    pred = make_prediction(song=song, artist=artist, track_id=track_id)
    predictions.append(
        {"song": song, "artist": artist, "track_id": track_id, "prediction": pred}
    )

    df = pd.DataFrame(predictions).sort_values("prediction", ascending=False)
    print(df)
