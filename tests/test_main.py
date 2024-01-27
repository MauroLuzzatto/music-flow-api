from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_get_main():
    response = client.get("/")
    assert response.status_code == 200


def test_get_health():
    response = client.get("/api/health")
    assert response.status_code == 200


def test_get_about():
    response = client.get("/about/")
    assert response.status_code == 200


def test_get_features():
    song = "The Less I Know The Better"
    artist = "Tame Impala"
    response = client.get(f"/api/features/?song={song}&artist={artist}")

    target_response = {
        "track": {
            "track_name": "The Less I Know The Better",
            "artist_name": "Tame Impala",
            "number_of_available_markets": 183,
            "num_artists": 1,
            "duration_ms": 216320,
            "explicit": True,
            "popularity": 88,
            "isrc": "AUUM71500303",
        },
        "album": {
            "release_date_precision": "day",
            "release_year": 2015,
            "release_month": 7,
            "release_day": 17,
            "date_is_complete": True,
            "album": "Currents",
        },
        "audio_features": {
            "danceability": 0.64,
            "energy": 0.74,
            "key": 4,
            "loudness": -4.083,
            "mode": 1,
            "speechiness": 0.0284,
            "acousticness": 0.0115,
            "instrumentalness": 0.00678,
            "liveness": 0.167,
            "valence": 0.785,
            "tempo": 116.879,
            "id": "6K4t31amVTZDgR3sKmwUJJ",
            "time_signature": 4,
        },
        "metadata": {
            "song": "The Less I Know The Better",
            "artist": ["Tame Impala"],
            "album": "Currents",
        },
    }
    assert response.status_code == 200
    assert response.json() == target_response


def test_read_raw_features():
    song = "The Less I Know The Better"
    artist = "Tame Impala"
    response = client.get(f"/api/raw_features/?song={song}&artist={artist}")
    assert response.status_code == 200


# def test_read_prediction():
#     artist = "Tame Impala"
#     song = "The Less I Know The Better"

#     response = client.get(f"/api/prediction/?song={song}&artist={artist}")

#     print(response)
#     print(response.url)
#     assert response.status_code == 200
#     assert response.json()["prediction"] < 10 and response.json()["prediction"] > 5
