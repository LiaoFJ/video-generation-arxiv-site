from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8000
    content_root: str = Field(default="content", alias="CONTENT_ROOT")
    publish_limit: int = 5
    keywords: list[str] = Field(
        default_factory=lambda: [
            "video generation",
            "text-to-video",
            "image-to-video",
            "video diffusion",
        ]
    )
    ranking_url_template: str | None = Field(default=None, alias="RANKING_URL_TEMPLATE")
    request_timeout_seconds: float = Field(default=30.0, alias="REQUEST_TIMEOUT_SECONDS")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.deepseek.com", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="deepseek-v4-flash", alias="OPENAI_MODEL")
