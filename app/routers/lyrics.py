from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from app.core.forms import SongRequestForm
from music_flow import Predictor
from music_flow.core.utils import map_score_to_emoji

base_path = Path("/home/maurol/track-recommender/app").absolute()
templates = Jinja2Templates(directory=str(base_path / "templates"))


translator_dict = {}

router = APIRouter(
    prefix="/form", tags=["form"], responses={404: {"description": "Not found"}}
)


@router.get("/about/")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@router.get("/")
def get_lyrics(request: Request):
    return templates.TemplateResponse("prediction.html", {"request": request})


@router.post("/")
async def post_lyrics(request: Request):

    form = SongRequestForm(request)
    await form.load_data()

    model_version = "0.1.0"
    predictor = Predictor(model_version)
    predictor.get_metdata()

    prediction = predictor.make_prediction(song=form.song, artist=form.artist)
    print(prediction)

    # if not prediction:
    #     raise HTTPException(status_code=404, detail="song not found")

    header = f"{form.song.capitalize()} by {form.artist.capitalize()}"

    if "error" in prediction:
        form.errors.append("Song not found.")
        return templates.TemplateResponse("prediction.html", form.__dict__)

    if form.is_valid():

        user_message = map_score_to_emoji(prediction["prediction"])
        prediction["message"] = user_message

        try:
            return templates.TemplateResponse(
                "success.html",
                {
                    "request": request,
                    "header": header,
                    "prediction": prediction,
                },
            )
        except Exception as e:
            form.errors.append(
                "You might not be logged in, In case problem persists please contact us."
            )
            print(e)
            return templates.TemplateResponse("prediction.html", form.__dict__)

    return templates.TemplateResponse("prediction.html", form.__dict__)
