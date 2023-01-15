import os
import pickle
from pprint import pprint

import numpy as np
import pandas as pd

from track_recommender.model.preprocessing import (
    feature_preprocessing,
    reverse_prediction,
)
from track_recommender.prepare_data.features.create_audio_features_dataset import (
    format_features,
)
from track_recommender.prepare_data.features.get_audio_features import get_features
from track_recommender.prepare_data.random_songs_from_playlist import (
    get_playlist_tracks,
)

folder = "2023-01-15--16-18-26"

path_results = f"/home/maurol/track-recommender/results/{folder}"
path_model = os.path.join(path_results, "XGBRegressor.pickle")

with open(path_model, "rb") as handle:
    estimator = pickle.load(handle)

song = "Home"
artist = "Caribou"


# song = "Never Fight A Man With A Perm"
# artist = "IDLES"

# song = "Penawar Duka"
# artist = "Reeka"


def make_prediction(song, artist, estimator):

    features = get_features(song, artist)
    audio_features = format_features(data=features, track_name=song, artist_name=artist)
    sample = pd.DataFrame(audio_features, index=[0])
    sample["plays"] = 0

    sample_formated, columns_scope = feature_preprocessing(sample)
    input_sample = sample_formated[columns_scope]

    scaled_prediction = estimator.predict(input_sample)
    prediction = reverse_prediction(scaled_prediction)
    return prediction


playlist_id = "37i9dQZEVXcJlIMuDHGHCM"
tracks = get_playlist_tracks(playlist_id)

predictions = []
for track in tracks[:]:
    print(track)

    song = track["track_name"]
    artist = track["artists"]

    pred = make_prediction(song=song, artist=artist, estimator=estimator)
    predictions.append({"song": song, "artist": artist, "prediction": pred})

df = pd.DataFrame(predictions).sort_values("prediction", ascending=False)


print(df)
