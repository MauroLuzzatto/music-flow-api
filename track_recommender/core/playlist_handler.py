import requests


class PlaylistHandler(object):
    def __init__(self, headers):
        self.headers = headers

    def get_request(self, url: str):
        response = requests.get(url=url, headers=self.headers)
        return response.json(), response.status_code

    def get_post(self, url: str, params=None):
        if not params:
            params = {}

        response = requests.post(url=url, headers=self.headers, json=params)
        return response.json(), response.status_code

    def get_playlists(self, user_id):
        # Second step – make a request tox any of the playlists endpoint. Make sure to set a valid value for <spotify_user>.
        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        response, status_code = self.get_request(url)
        return response, status_code

    def get_playlist_items(self, playlist_id, limit=100, offset=0):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit={limit}&offset={offset}"
        response, status_code = self.get_request(url)
        return response, status_code

    def create_playlist(self, user_id, params):

        url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        response, status_code = self.get_post(url, params)
        return response, status_code

    def add_tracks_to_playlist(self, playlist_id, track_ids):

        uris = [f"spotify:track:{track_id}" for track_id in track_ids]
        params = {"uris": uris}

        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        response, status_code = self.get_post(url, params=params)
        return response, status_code
