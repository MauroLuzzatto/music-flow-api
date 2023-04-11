import json
import os

import requests
from dotenv import load_dotenv
from ratelimiter import RateLimiter
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from music_flow.core.utils import path_env

load_dotenv(path_env)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")


limiter = RateLimiter(max_calls=2000, period=3600)


class SpotifyAPI(object):
    def __init__(self):
        self.headers = self.get_headers()
        retry = Retry(connect=3, backoff_factor=0.5)
        self.adapter = HTTPAdapter(max_retries=retry)

    def get_headers(self):
        grant_type = "client_credentials"
        body_params = {"grant_type": grant_type}
        auth = (CLIENT_ID, CLIENT_SECRET)

        url = "https://accounts.spotify.com/api/token"
        response = requests.post(url, data=body_params, auth=auth, verify=True)  # type: ignore

        if response.status_code != 200:
            print("bad credentials")
            print(response)
            exit(1)

        token = json.loads(response.text)["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    @limiter
    def get_request(self, url: str):
        """TODO: move to Base class"""
        with requests.Session() as session:
            session.mount("https://", self.adapter)
            response = session.get(url=url, headers=self.headers)

        return response.json(), response.status_code

    @limiter
    def get_post(self, url: str, params=None):
        """TODO: move to Base class"""
        if not params:
            params = {}

        with requests.Session() as session:
            session.mount("https://", self.adapter)
            response = session.post(url=url, headers=self.headers, json=params)
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

    def get_track_info(self, track, artist, limit=4):
        url = f"https://api.spotify.com/v1/search?q=track:{track}%20artist:{artist}&limit={limit}&type=track"
        response, status_code = self.get_request(url)
        return response, status_code

    def get_track(self, id):
        url = f"https://api.spotify.com/v1/tracks/{id}"
        response, status_code = self.get_request(url)
        return response, status_code

    def get_audio_features(self, id):
        url = f"https://api.spotify.com/v1/audio-features/{id}"
        response, status_code = self.get_request(url)
        return response, status_code

    def get_albums(self, id):
        url = f"https://api.spotify.com/v1/albums/{id}"
        response, status_code = self.get_request(url)
        return response, status_code

    def search_track_url(self, track, artist=None):
        artist = "" if not artist else artist
        track = self.clean_string(track)
        artist = self.clean_string(artist)
        return f"https://api.spotify.com/v1/search?q=track:{track} artist:{artist}&type=track"

    def get_audio_analysis(self, id):
        url = f"https://api.spotify.com/v1/audio-analysis/{id}"
        response, status_code = self.get_request(url)
        return response, status_code

    @staticmethod
    def clean_string(string):
        return (
            string.replace("'", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace("#", "")
            .replace("-", "")
            .replace("&", "")
            .replace("'", "")
        )
