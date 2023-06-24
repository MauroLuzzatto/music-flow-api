from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional


# --------------------------------------------------------------------------------
# Router
# --------------------------------------------------------------------------------

router = APIRouter(prefix="/api", tags=["API"])
