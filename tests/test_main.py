from pprint import pprint

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_read_health():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_read_features():
    song = "The Less I Know The Better"
    artist = "Tame Impala"
    response = client.get(f"/api/features/?song={song}&artist={artist}")

    pprint(response.json())

    # target_response = {
    #     "track": {
    #         "track_name": "The Less I Know The Better",
    #         "artist_name": "Tame Impala",
    #         "number_of_available_markets": 183,
    #         "num_artists": 1,
    #         "duration_ms": 216320,
    #         "explicit": True,
    #         "popularity": 82,
    #         "isrc": "AUUM71500303",
    #     },
    #     "album": {
    #         "release_date_precision": "day",
    #         "release_date": "2015-07-17",
    #         "release_year": 2015,
    #         "release_month": 7,
    #         "release_day": 17,
    #         "date_is_complete": True,
    #         "album": "Currents",
    #     },
    #     "audio_features": {
    #         "danceability": 0.64,
    #         "energy": 0.74,
    #         "key": 4,
    #         "loudness": -4.083,
    #         "mode": 1,
    #         "speechiness": 0.0284,
    #         "acousticness": 0.0115,
    #         "instrumentalness": 0.00678,
    #         "liveness": 0.167,
    #         "valence": 0.785,
    #         "tempo": 116.879,
    #         "type": "audio_features",
    #         "id": "6K4t31amVTZDgR3sKmwUJJ",
    #         "uri": "spotify:track:6K4t31amVTZDgR3sKmwUJJ",
    #         "track_href": "https://api.spotify.com/v1/tracks/6K4t31amVTZDgR3sKmwUJJ",
    #         "analysis_url": (
    #             "https://api.spotify.com/v1/audio-analysis/6K4t31amVTZDgR3sKmwUJJ"
    #         ),
    #         "duration_ms": 216320,
    #         "time_signature": 4,
    #     },
    # }
    print("test", response.json())
    assert response.status_code == 200
    # assert response.json() == target_response


def test_read_raw_features():
    song = "The Less I Know The Better"
    artist = "Tame Impala"
    response = client.get(f"/api/raw_features/?song={song}&artist={artist}")
    assert response.status_code == 200


# def test_read_prediction():
#     song = "The Less I Know The Better"
#     artist = "Tame Impala"

#     # TODO: make test smarter for predictions
#     target_response = {
#         "song": "The Less I Know The Better",
#         "artist": "Tame Impala",
#         "prediction": 5.35,
#         "description": (
#             "The predicted number of future streams of the song based on the Spotify"
#             " API audio features."
#         ),
#         "song_metadata": {
#             "song": "The Less I Know The Better",
#             "artist": ["Tame Impala"],
#             "album": "Currents",
#         },
#         "message": {"emoji": "😍", "text": "What a banger!"},
#     }

#     with TestClient(app) as client:
#         response = client.get(f"/prediction/?song={song}&artist={artist}")

#         pprint(response)
#         assert response.status_code == 200
#         # assert response.json() == target_response
