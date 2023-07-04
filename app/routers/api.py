import logging

from fastapi import APIRouter, HTTPException, Request

from app.__init__ import __version__ as api_version
from app.config import settings
from app.schemas import Features, Health
from app.utils.response_formatter import prepare_raw_features_response
from app.utils.response_messages import get_exception_details
from music_flow import get_formatted_features, get_raw_features
from music_flow.__init__ import __version__ as model_version

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)


router: APIRouter = APIRouter(prefix="/api", tags=["API"])


@router.get("/info")
async def info() -> dict:
    """Get the root of the API"""
    return {"message": settings.MESSAGE}


@router.get("/health")
async def health_api() -> Health:
    """Get the health of the API"""
    health = Health(
        name=settings.PROJECT_NAME,
        description=settings.API_DESCRIPTION,
        api_version=api_version,
        model_version=model_version,
        project_url=settings.GITHUB_URL,
    )
    return health


@router.get("/raw_features/")
async def get_raw_features_api(song: str, artist: str) -> dict:
    """
    Get the raw audio features of a song from the Spotify API

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song or audio features could not be found or fetched from Spotify API

    Returns:
        dict: dict with raw features
    """
    raw_features, status_code = get_raw_features(song, artist)

    if raw_features["status"] != "success":
        detail = prepare_raw_features_response(raw_features, status_code)
        raise HTTPException(status_code=status_code, detail=detail)

    return raw_features


@router.get("/features/")
async def get_features_api(song: str, artist: str) -> Features:
    """
    Get the preprocessed audio features that are used for making predictions

    Args:
        song (str): name of the song
        artist (str): artist of the song

    Raises:
        HTTPException: if the song or audio features could not be found or fetched from Spotify API
            or if formatting of the features failed

    Returns:
        Features: features object
    """
    raw_features = await get_raw_features_api(song, artist)
    features = get_formatted_features(data=raw_features, is_flattened=False)
    if not features:
        status_code = 500
        detail = get_exception_details("formating_failure", status_code)
        raise HTTPException(status_code=status_code, detail=detail)
    return Features(**features)
