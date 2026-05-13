from pathlib import Path

from fastapi import FastAPI

from app.config import Settings
from app.web.routes import build_router


def create_app(content_root: Path | None = None, settings: Settings | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(build_router(content_root=content_root, settings=settings))
    return app


app = create_app()
