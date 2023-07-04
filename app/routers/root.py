import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

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
    "failed_to_fetch_song": "Failed to fetch song. Please check for typos or try another one.",
}


router = APIRouter(tags=["FORM"])


@router.get("/")
async def get_form(request: Request) -> Jinja2Templates:
    return templates.TemplateResponse("prediction.html", {"request": request})


@router.post("/")
async def post_form(request: Request) -> Jinja2Templates:
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """

    form = SongRequestForm(request)
    await form.load_data()
    logger.debug(f"form: {form.__dict__}")

    from main import get_prediction_api

    try:
        output = await get_prediction_api(song=form.song, artist=form.artist)  # type: ignore
    except HTTPException:
        form.errors.append(erros["failed_to_fetch_song"])
        return templates.TemplateResponse("prediction.html", form.__dict__)

    if form.is_valid():
        header = f"{form.song.capitalize()} by {form.artist.capitalize()}"  # type: ignore
        prediction = output.dict()

        payload = {
            "request": request,
            "header": header,
            "prediction": prediction,
        }

        try:
            return templates.TemplateResponse("success.html", payload)
        except Exception as e:
            form.errors.append(erros["generic_error"])
            logger.error(e)
            return templates.TemplateResponse("prediction.html", form.__dict__)

    return templates.TemplateResponse("prediction.html", form.__dict__)


@router.get("/about/")
async def get_about(request: Request) -> Jinja2Templates:
    return templates.TemplateResponse("about.html", {"request": request})
