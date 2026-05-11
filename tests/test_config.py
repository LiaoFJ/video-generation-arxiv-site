from app.config import Settings


def test_settings_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTENT_ROOT", str(tmp_path / "content"))
    settings = Settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.content_root == str(tmp_path / "content")
    assert settings.publish_limit == 5
    assert settings.keywords == [
        "video generation",
        "text-to-video",
        "image-to-video",
        "video diffusion",
    ]
    assert settings.openai_base_url == "https://api.deepseek.com"
    assert settings.openai_model == "deepseek-v4-flash"
