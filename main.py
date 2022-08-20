import os
from pathlib import Path
from typing import Optional

import lyricsgenius
import uvicorn
from core.config import settings
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from song_translator.translation.translation import (
    get_translation, get_translator_by_language)

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)
GENIUS_ACCESS_TOKEN = os.getenv("API_KEY")


# with open(os.path.join(os.getcwd(), "app", "song_translator", "genius", "API_KEY.txt"), mode="r") as f:
#     GENIUS_ACCESS_TOKEN = f.read()

BASE_PATH = Path(__file__).resolve().parent

translator_dict = {}

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_PATH / "static")),
    name="static",
)

templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))


@app.get("/")
def home():
    return {"hello": "world"}


@app.get("/about", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


from fastapi import FastAPI, Form, Request


@app.get("/form")
def form_post(request: Request):
    result = "Type a number"
    return templates.TemplateResponse(
        "form.html", context={"request": request, "result": result}
    )


@app.post("/form")
def form_post(request: Request, num: int = Form(...)):
    result = f"cool {num}"
    return templates.TemplateResponse(
        "form.html", context={"request": request, "result": result}
    )


def split_lyrics(text):
    return text.replace("[", "\n----\n[").split("\n")


@app.get("/lyrics", response_class=HTMLResponse)
def get_lyrics(
    request: Request,
    artist: str,
    song: str,
):
    """[summary]

    Args:
        request (Request): [description]
        artist (str): [description]
        song (str): [description]

    Raises:
        HTTPException: [description]

    Returns:
        [type]: [description]

    """
    if not isinstance(song, str) or not isinstance(artist, str):
        raise HTTPException(status_code=404, detail="song not found")

    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    song_instance = genius.search_song(song, artist, get_full_info=False)

    header = f"'{song}' by '{artist}'"
    lyrics = split_lyrics(song_instance.lyrics)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "header": header, "lyrics": lyrics, "language": "en"},
    )


@app.get("/translate", response_class=HTMLResponse)
def get_translate(request: Request, artist: str, song: str, language: str = "en"):
    """[summary]

    Args:
        request (Request): [description]
        artist (str): [description]
        song (str): [description]

    Raises:
        HTTPException: [description]

    Returns:
        [type]: [description]
    """

    if not isinstance(song, str) or not isinstance(artist, str):
        raise HTTPException(status_code=404, detail="song not found")

    genius = lyricsgenius.Genius(GENIUS_ACCESS_TOKEN)
    song_instance = genius.search_song(song, artist, get_full_info=False)
    header = f"'{song}' by '{artist}'"
    lyrics = song_instance.lyrics

    if language != "en":
        if not translator_dict.get(language, None):
            translator_dict[language] = get_translator_by_language(language)
        lyrics = get_translation(lyrics, translator_dict[language])

    lyrics = split_lyrics(lyrics)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "header": header, "lyrics": lyrics, "language": language},
    )


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
