from fastapi import APIRouter
from pydantic import BaseModel

from app import __version__
from app.core.settings import get_settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    app_env: str


@router.get("/health", response_model=HealthResponse)
def health():
    settings = get_settings()
    return HealthResponse(status="ok", version=__version__, app_env=settings.app_env)
