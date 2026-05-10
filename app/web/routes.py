import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


def build_router(content_root: Path | None = None) -> APIRouter:
    router = APIRouter()
    root = content_root or Path("content")
    templates = Jinja2Templates(directory="app/templates")

    @router.get("/", response_class=HTMLResponse)
    def index(request: Request):
        entries = []
        for index_file in sorted(root.glob("*/index.json"), reverse=True):
            entries.extend(json.loads(index_file.read_text(encoding="utf-8")))
        return templates.TemplateResponse(request, "index.html", {"entries": entries})

    @router.get("/archive/{archive_date}", response_class=HTMLResponse)
    def archive(request: Request, archive_date: str):
        index_file = root / archive_date / "index.json"
        if not index_file.exists():
            raise HTTPException(status_code=404)
        entries = json.loads(index_file.read_text(encoding="utf-8"))
        return templates.TemplateResponse(
            request,
            "archive.html",
            {"entries": entries, "archive_date": archive_date},
        )

    @router.get("/papers/{archive_date}/{slug}", response_class=HTMLResponse)
    def paper_detail(request: Request, archive_date: str, slug: str):
        detail_file = root / archive_date / f"{slug}.json"
        if not detail_file.exists():
            raise HTTPException(status_code=404)
        paper = json.loads(detail_file.read_text(encoding="utf-8"))
        return templates.TemplateResponse(request, "paper.html", {"paper": paper})

    return router
