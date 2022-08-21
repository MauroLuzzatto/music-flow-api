import hashlib
import json
import os

import pandas as pd
from dotenv import load_dotenv
from spotify_api import SpotifyAPI

dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
)

print(dotenv_path)
load_dotenv(dotenv_path)


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

track = "one more time"
artist = "daft punk"

spotify_api = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)
url = spotify_api.search_track_url(track, artist)
r = spotify_api.get_request(url)
id = spotify_api.get_track_id(r)
print(r, id)
