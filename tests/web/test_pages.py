import json

from fastapi.testclient import TestClient

from app.main import create_app


def test_index_page_renders_published_paper(tmp_path):
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

    app = create_app(content_root=tmp_path)
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "Paper A" in response.text
    assert "2026-05-09" in response.text
    assert "https://arxiv.org/abs/2505.00001" in response.text

    archive_response = client.get("/archive/2026-05-10")
    assert archive_response.status_code == 200
    assert "2505-00001" in archive_response.text

    detail_response = client.get("/papers/2026-05-10/2505-00001")
    assert detail_response.status_code == 200
    assert "中文摘要" in detail_response.text
    assert "现有视频生成方法在时序一致性上存在明显问题。" in detail_response.text
    assert "论文通过显式的时序模块和条件控制来稳定生成过程。" in detail_response.text
    assert "https://arxiv.org/abs/2505.00001" in detail_response.text
