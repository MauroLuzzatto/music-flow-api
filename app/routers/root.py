
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, RedirectResponse
from typing import Optional


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter()


# --------------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------------

@router.get(
  path="/",
  summary="Redirects to the login or reminders pages",
  tags=["Pages"]
)