import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.highscore import Highscore
from app.utils.song_request_form import SongRequestForm
from music_flow.core.utils import path_app

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

base_path = Path(path_app).absolute()
templates = Jinja2Templates(directory=str(base_path / "templates"))

erros = {
    "song_not_found": "Song not found.",
    "generic_error": "OPS, Something went wrong. Please try again.",
    "failed_to_fetch_song": "Failed to fetch song. Please check for typos or try another song.",
}


router = APIRouter(tags=["FORM"])


@router.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """
    is_reset = "resetButton" == request.headers.get("HX-Trigger")
    highscore = Highscore(request, is_reset=is_reset)

    payload = {
        "request": request,
        "scores": highscore.get_highscore(),
    }
    template = "prediction.html"
    return templates.TemplateResponse(template, payload)


@router.get("/about/", response_class=HTMLResponse)
async def get_about(request: Request):
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """
    return templates.TemplateResponse("about.html", {"request": request})


@router.post("/search_song")
async def get_success_endpoint(request: Request):
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """
    template = "partials/songform.html"
    form = SongRequestForm(request)
    await form.load_data()

    if not form.is_valid():
        payload = form.as_dict()
        return templates.TemplateResponse(template, payload)

    logger.debug(f"form: {form.as_dict()}")

    from main import get_prediction_api

    try:
        output = await get_prediction_api(song=form.song, artist=form.artist)  # type: ignore
    except HTTPException:
        form.errors.append(erros["failed_to_fetch_song"])
        payload = form.as_dict()
        del payload["song"]
        del payload["artist"]
        return templates.TemplateResponse(template, payload)

    header = f'"{form.song.capitalize()}" by "{form.artist.capitalize()}"'  # type: ignore
    response = output.dict()

    highscore = Highscore(request)
    id = header
    _prediction = response["prediction"]
    highscore.add_score(id, _prediction, header)

    payload = {
        "request": request,
        "header": header,
        "prediction": response,
        "scores": highscore.get_highscore(),
    }
    try:
        template = "partials/success.html"
        return templates.TemplateResponse(template, payload)
    except Exception as e:
        form.errors.append(erros["generic_error"])
        logger.error(e)
        return templates.TemplateResponse(template, payload)
