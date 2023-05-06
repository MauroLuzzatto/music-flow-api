from music_flow.core.playlists.get_playlist_tracks import get_playlist_tracks
from music_flow.core.spotify_api import SpotifyAPI
from music_flow.core.predictor import Predictor

model_folder = "2023-01-21--12-33-25"
user_id = "1157239771"
playlist_id = "37i9dQZEVXcJlIMuDHGHCM"

spotifAPI = SpotifyAPI()
paylist, status_code = spotifAPI.get_playlist_items(playlist_id=playlist_id)
tracks = get_playlist_tracks(paylist)

predictor = Predictor(model_folder)

predictions = []
for track in tracks[:4]:
    song = track["track_name"]
    artist = track["artists"]
    track_id = track["track_id"]
    print(song, artist, track_id)

    data = predictor.predict(song=song, artist=artist, track_id=track_id)
    print(data)
