from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.core.song_request_form import SongRequestForm
from music_flow.core.utils import path_app

base_path = Path(path_app).absolute()
templates = Jinja2Templates(directory=str(base_path / "templates"))


song_not_found_error = "Song not found."
generic_error = "OPS, Something went wrong. Please try again."
failed_to_fetch_song_error = "Failed to fetch song. Please try another one."


router = APIRouter(
    prefix="/form", tags=["form"], responses={404: {"description": "Not found"}}
)


@router.get("/about/")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@router.get("/")
def get_song(request: Request):
    return templates.TemplateResponse("prediction.html", {"request": request})


@router.post("/")
async def post_form(request: Request):
    """_summary_

    Args:
        request (Request): _description_

    Returns:
        _type_: _description_
    """

    form = SongRequestForm(request)
    await form.load_data()

    from main import get_prediction_api

    try:
        output = await get_prediction_api(song=form.song, artist=form.artist)  # type: ignore
    except HTTPException:
        form.errors.append(failed_to_fetch_song_error)
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
            form.errors.append(generic_error)
            print(e)
            return templates.TemplateResponse("prediction.html", form.__dict__)

    return templates.TemplateResponse("prediction.html", form.__dict__)
