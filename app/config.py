from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = "127.0.0.1"
    port: int = 8000
    content_root: str = Field(default="content", alias="CONTENT_ROOT")
    publish_limit: int = 5
    categories: list[str] = Field(default_factory=lambda: ["cs.CV", "cs.AI", "cs.LG"])
    keywords: list[str] = Field(
        default_factory=lambda: [
            "video generation",
            "text-to-video",
            "image-to-video",
            "video diffusion",
        ]
    )
