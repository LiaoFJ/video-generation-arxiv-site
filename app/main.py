from pathlib import Path

from fastapi import FastAPI

from app.web.routes import build_router


def create_app(content_root: Path | None = None) -> FastAPI:
    app = FastAPI()
    app.include_router(build_router(content_root=content_root))
    return app


app = create_app()
