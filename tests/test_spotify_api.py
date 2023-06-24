from pprint import pprint

from music_flow.core.spotify_api import SpotifyAPI

spotify_api = SpotifyAPI()


def test_search_track_url():
    track = "one more time"
    artist = "daft punk"
    url = spotify_api.search_track_url(track, artist)
    response, status_code = spotify_api.get_request(url)
    assert (
        url
        == "https://api.spotify.com/v1/search?q=track:one more time artist:daft punk&type=track"
    )
    assert status_code == 200
    assert (
        response["tracks"]["href"]
        == "https://api.spotify.com/v1/search?query=track%3Aone+more+time+artist%3Adaft+punk&type=track&offset=0&limit=20"
    )


def test_track_endpoint():
    id = "6K4t31amVTZDgR3sKmwUJJ"
    response, status_code = spotify_api.get_track(id)

    pprint(response)
    assert status_code == 200
    assert set(response.keys()) == {
        "album",
        "artists",
        "available_markets",
        "disc_number",
        "duration_ms",
        "explicit",
        "external_ids",
        "external_urls",
        "href",
        "id",
        "is_local",
        "name",
        "popularity",
        "preview_url",
        "track_number",
        "type",
        "uri",
    }
