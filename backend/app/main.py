import logging
import time

from fastapi import FastAPI, Request

from app import __version__
from app.api.health import router as health_router
from app.core.logging_setup import log_event, setup_logging
from app.core.settings import get_settings


def create_app() -> FastAPI:
    # Bad settings raise an error here, so the app does not start.
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger("app")

    app = FastAPI(title="Domain RAG Copilot API", version=__version__)
    app.include_router(health_router)

    # CORS is not enabled yet. When the frontend is added (Stage 13), allow
    # only settings.frontend_origin.

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        # Only the method, path and status are logged. Bodies are never logged.
        log_event(
            logger,
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    log_event(logger, "app_started", app_env=settings.app_env)
    return app


app = create_app()
