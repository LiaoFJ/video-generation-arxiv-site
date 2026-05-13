import base64
import hashlib
import hmac
import time

from fastapi import Request

from app.config import Settings

AUTH_COOKIE_NAME = "video_generation_auth"
AUTH_COOKIE_MAX_AGE = 60 * 60 * 24 * 7


def credentials_configured(settings: Settings) -> bool:
    return bool(settings.app_username and settings.app_password)


def verify_credentials(username: str, password: str, settings: Settings) -> bool:
    return bool(
        settings.app_username
        and settings.app_password
        and hmac.compare_digest(username, settings.app_username)
        and hmac.compare_digest(password, settings.app_password)
    )


def build_auth_cookie(settings: Settings) -> str:
    if not settings.app_username or not settings.app_password:
        raise ValueError("APP_USERNAME and APP_PASSWORD must be configured.")

    expires_at = int(time.time()) + AUTH_COOKIE_MAX_AGE
    payload = f"{settings.app_username}:{expires_at}"
    signature = hmac.new(
        settings.app_password.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token.encode("utf-8")).decode("utf-8")


def get_authenticated_username(request: Request, settings: Settings) -> str | None:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token or not settings.app_username or not settings.app_password:
        return None

    try:
        decoded = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
        username, expires_at_text, signature = decoded.rsplit(":", 2)
        payload = f"{username}:{expires_at_text}"
        expected_signature = hmac.new(
            settings.app_password.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_signature):
            return None
        if int(expires_at_text) < int(time.time()):
            return None
        if not hmac.compare_digest(username, settings.app_username):
            return None
        return username
    except (ValueError, TypeError):
        return None
