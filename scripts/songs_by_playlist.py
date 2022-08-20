from collections.abc import MutableMapping
from pprint import pprint

import pandas as pd
from spotify.access_api_spotify import CLIENT_ID, CLIENT_SECRET, SpotifyAPI

USER_ID = 1157239771
playlist_id = "6KOwiWg5zwrt83nEcx7HyI"
playlist_id = "37i9dQZF1DXbTxeAdrVG2l"


spotifAPI = SpotifyAPI(CLIENT_ID, CLIENT_SECRET)

paylist = spotifAPI.get_playlist_items(playlist_id=playlist_id, limit=4, offset=4)
# df = pd.DataFrame(paylist)
# print(list(df))


def delete_keys_from_dict(dictionary, keys):
    keys_set = set(keys)  # Just an optimization for the "if key in keys" lookup.

    modified_dict = {}
    for key, value in dictionary.items():
        if key not in keys_set:
            if isinstance(value, MutableMapping):
                modified_dict[key] = delete_keys_from_dict(value, keys_set)
            else:
                modified_dict[
                    key
                ] = value  # or copy.deepcopy(value) if a copy is desired for non-dicts.
    return modified_dict


tracks = []


for track in paylist["items"]:
    print("---" * 10)

    # new_dict = delete_keys_from_dict(track["track"], ["available_markets"])
    # pprint(new_dict)

    # for key in track["track"]:
    #     print("\n", key)
    #     pprint(track["track"][key])

    artists = [artist["name"] for artist in track["track"]["artists"]]
    song = track["track"]["name"]
    album = track["track"]["album"]["name"]
    release_date = track["track"]["album"]["release_date"]

    track_dict = {
        "artists": artists,
        "song": song,
        "album": album,
        "release_date": release_date,
    }
    tracks.append(track_dict)


pprint(tracks)
import lyricsgenius

GENIUS_ACCESS_TOKEN = "M8Mx-chqYBeQzMuQnzmGQkysr0T2-1yJrPohkPUQxh58iUcFMegCdWIYbQ1lQu3_"

for track in tracks:

    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)

    song_instance = genius.search_song(song=track["song"], artist=track["artist"][0])
    lyrics = song_instance.lyrics
    print(lyrics)
