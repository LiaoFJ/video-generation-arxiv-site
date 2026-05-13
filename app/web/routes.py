import json
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.web.auth import (
    AUTH_COOKIE_MAX_AGE,
    AUTH_COOKIE_NAME,
    build_auth_cookie,
    credentials_configured,
    get_authenticated_username,
    verify_credentials,
)


def build_router(content_root: Path | None = None, settings: Settings | None = None) -> APIRouter:
    router = APIRouter()
    root = content_root or Path("content")
    templates = Jinja2Templates(directory="app/templates")

    def get_settings() -> Settings:
        return settings or Settings()

    def render_template(request: Request, template_name: str, context: dict, status_code: int = 200):
        active_settings = get_settings()
        username = get_authenticated_username(request, active_settings)
        return templates.TemplateResponse(
            request,
            template_name,
            {
                **context,
                "current_user": username,
                "credentials_configured": credentials_configured(active_settings),
            },
            status_code=status_code,
        )

    def require_login(request: Request):
        if get_authenticated_username(request, get_settings()):
            return None
        return RedirectResponse(url="/login", status_code=303)

    @router.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        if get_authenticated_username(request, get_settings()):
            return RedirectResponse(url="/", status_code=303)
        return render_template(
            request,
            "login.html",
            {"error_message": None},
        )

    @router.post("/login", response_class=HTMLResponse)
    async def login(request: Request):
        active_settings = get_settings()
        body = (await request.body()).decode("utf-8")
        form_data = parse_qs(body)
        username = form_data.get("username", [""])[0].strip()
        password = form_data.get("password", [""])[0]

        if not credentials_configured(active_settings):
            return render_template(
                request,
                "login.html",
                {"error_message": "站点尚未配置登录账号，请先检查 .env。"},
                status_code=500,
            )

        if not verify_credentials(username, password, active_settings):
            return render_template(
                request,
                "login.html",
                {"error_message": "用户名或密码错误"},
                status_code=200,
            )

        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(
            AUTH_COOKIE_NAME,
            build_auth_cookie(active_settings),
            max_age=AUTH_COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
        return response

    @router.post("/logout")
    def logout():
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(AUTH_COOKIE_NAME)
        return response

    @router.get("/", response_class=HTMLResponse)
    def index(request: Request):
        redirect = require_login(request)
        if redirect:
            return redirect

        entries = []
        archive_dates = sorted((path.parent.name for path in root.glob("*/index.json")), reverse=True)
        for archive_date in archive_dates:
            index_file = root / archive_date / "index.json"
            entries.extend(json.loads(index_file.read_text(encoding="utf-8")))

        featured_entry = entries[0] if entries else None
        latest_archive_date = archive_dates[0] if archive_dates else None
        return render_template(
            request,
            "index.html",
            {
                "entries": entries,
                "featured_entry": featured_entry,
                "latest_archive_date": latest_archive_date,
                "entry_count": len(entries),
            },
        )

    @router.get("/archive/{archive_date}", response_class=HTMLResponse)
    def archive(request: Request, archive_date: str):
        redirect = require_login(request)
        if redirect:
            return redirect

        index_file = root / archive_date / "index.json"
        if not index_file.exists():
            raise HTTPException(status_code=404)
        entries = json.loads(index_file.read_text(encoding="utf-8"))
        return render_template(
            request,
            "archive.html",
            {"entries": entries, "archive_date": archive_date},
        )

    @router.get("/papers/{archive_date}/{slug}", response_class=HTMLResponse)
    def paper_detail(request: Request, archive_date: str, slug: str):
        redirect = require_login(request)
        if redirect:
            return redirect

        detail_file = root / archive_date / f"{slug}.json"
        if not detail_file.exists():
            raise HTTPException(status_code=404)
        paper = json.loads(detail_file.read_text(encoding="utf-8"))
        return render_template(request, "paper.html", {"paper": paper})

    return router
