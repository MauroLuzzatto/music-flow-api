import html
from typing import List, Optional

from fastapi import Request


class SongRequestForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.errors: List = []
        self.song: Optional[str] = None
        self.artist: Optional[str] = None

    async def load_data(self):
        form = await self.request.form()
        self.song = form.get("song")
        self.artist = form.get("artist")

    def is_valid(self):
        
        if not self.song or self.number_of_tokens(self.song) > 10:
            self.errors.append("A valid song is required")
        if not self.artist or self.number_of_tokens(self.artist) > 5:
            self.errors.append("A valid artist is required")
        if not self.errors:
            return True
        return False

    @staticmethod
    def number_of_tokens(string):
        return len(string.split())
