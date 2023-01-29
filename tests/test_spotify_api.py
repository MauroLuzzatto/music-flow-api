from music_flow.core.spotify_api import SpotifyAPI

track = "one more time"
artist = "daft punk"

spotify_api = SpotifyAPI()
url = spotify_api.search_track_url(track, artist)
r = spotify_api.get_request(url)
print(r)
