from typing import List, Optional

from fastapi import Request


class SongRequestForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List[str] = []
        self.song: Optional[str] = None
        self.artist: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.song = form.get("song")  # type: ignore
        self.artist = form.get("artist")  # type: ignore

    def is_valid(self):
        if not self.song and self.number_of_tokens(self.song) > 10:
            song_error = "A valid song is required"
            self.errors.append(song_error)

        if not self.artist and self.number_of_tokens(self.artist) > 5:
            aritst_error = "A valid artist is required"
            self.errors.append(aritst_error)

        if self.errors:
            return False
        return True

    def as_dict(self):
        return self.__dict__

    @staticmethod
    def number_of_tokens(string: str) -> int:
        return len(string.split())
