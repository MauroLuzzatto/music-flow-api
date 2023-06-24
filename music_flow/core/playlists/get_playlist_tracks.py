from typing import List


def get_playlist_tracks(paylist) -> List[dict]:
    print([track["track"]["name"] for track in paylist["items"]])
    print(len(paylist["items"]))

    if not paylist["items"]:
        return []

    tracks = []
    for track in paylist["items"]:
        try:
            artists = [artist["name"] for artist in track["track"]["artists"]][0]
        except IndexError:
            artists = None

        track_dict = {
            "track_id": track["track"]["id"],
            "artists": artists,
            "track_name": track["track"]["name"],
            "album": track["track"]["album"]["name"],
            "release_date": track["track"]["album"]["release_date"],
            "added_at": track["added_at"],
            "duration_ms": track["track"]["duration_ms"],
            "explicit": track["track"]["explicit"],
            "popularity": track["track"]["popularity"],
            "type": track["track"]["type"],
            "track": track["track"]["track"],
        }
        tracks.append(track_dict)

    return tracks
