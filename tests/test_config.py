from app.config import Settings


def test_settings_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv("CONTENT_ROOT", str(tmp_path / "content"))
    settings = Settings()

    assert settings.host == "127.0.0.1"
    assert settings.port == 8000
    assert settings.publish_limit == 5
    assert settings.categories == ["cs.CV", "cs.AI", "cs.LG"]
    assert "video generation" in settings.keywords
