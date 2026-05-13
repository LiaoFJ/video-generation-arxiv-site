import json

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def build_authenticated_client(tmp_path):
    archive_dir = tmp_path / "2026-05-10"
    archive_dir.mkdir(parents=True)
    (archive_dir / "2505-00001.json").write_text(
        json.dumps(
            {
                "slug": "2505-00001",
                "title": "Paper A",
                "arxiv_id": "2505.00001",
                "source_url": "https://arxiv.org/abs/2505.00001",
                "pdf_url": "https://arxiv.org/pdf/2505.00001.pdf",
                "authors": ["Ada"],
                "published_at": "2026-05-08T00:00:00Z",
                "archived_at": "2026-05-10",
                "traffic_date": "2026-05-09",
                "view_rank": 1,
                "view_count": 1234,
                "summary_zh": "中文摘要",
                "one_sentence_takeaway": "一句话结论",
                "problem_statement_zh": "现有视频生成方法在时序一致性上存在明显问题。",
                "core_design_zh": "论文通过显式的时序模块和条件控制来稳定生成过程。",
                "method_highlights": ["亮点 A"],
                "applications": ["应用 A"],
                "limitations": ["局限 A"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (archive_dir / "index.json").write_text(
        json.dumps(
            [
                {
                    "slug": "2505-00001",
                    "title": "Paper A",
                    "arxiv_id": "2505.00001",
                    "source_url": "https://arxiv.org/abs/2505.00001",
                    "published_at": "2026-05-08T00:00:00Z",
                    "archived_at": "2026-05-10",
                    "traffic_date": "2026-05-09",
                    "view_rank": 1,
                    "view_count": 1234,
                    "one_sentence_takeaway": "一句话结论",
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    settings = Settings(
        CONTENT_ROOT=str(tmp_path),
        APP_USERNAME="admin",
        APP_PASSWORD="secret-pass",
    )
    app = create_app(content_root=tmp_path, settings=settings)
    client = TestClient(app)
    return client


def test_protected_routes_redirect_to_login(tmp_path):
    client = build_authenticated_client(tmp_path)

    response = client.get("/", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_login_failure_shows_error(tmp_path):
    client = build_authenticated_client(tmp_path)

    response = client.post(
        "/login",
        content="username=admin&password=wrong-pass",
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert "用户名或密码错误" in response.text


def test_login_logout_and_render_authenticated_pages(tmp_path):
    client = build_authenticated_client(tmp_path)

    login_response = client.post(
        "/login",
        content="username=admin&password=secret-pass",
        headers={"content-type": "application/x-www-form-urlencoded"},
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/"

    response = client.get("/")
    assert response.status_code == 200
    assert "Video Generation Daily Brief" in response.text
    assert "Paper A" in response.text
    assert "原文链接" in response.text
    assert "退出登录" in response.text

    archive_response = client.get("/archive/2026-05-10")
    assert archive_response.status_code == 200
    assert "归档" in archive_response.text

    detail_response = client.get("/papers/2026-05-10/2505-00001")
    assert detail_response.status_code == 200
    assert "文章痛点" in detail_response.text
    assert "核心设计" in detail_response.text
    assert "https://arxiv.org/abs/2505.00001" in detail_response.text

    logout_response = client.post("/logout", follow_redirects=False)
    assert logout_response.status_code == 303
    assert logout_response.headers["location"] == "/login"

    protected_response = client.get("/", follow_redirects=False)
    assert protected_response.status_code == 303
    assert protected_response.headers["location"] == "/login"
