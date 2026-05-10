import json

from app.pipeline.publisher import publish_paper
from app.pipeline.schemas import SummaryResult


def test_publish_paper_writes_index_and_detail(tmp_path):
    summary = SummaryResult(
        summary_zh="中文摘要",
        one_sentence_takeaway="一句话结论",
        method_highlights=["亮点 A"],
        applications=["应用 A"],
        limitations=["局限 A"],
    )

    publish_paper(
        content_root=tmp_path,
        archive_date="2026-05-10",
        paper={
            "slug": "2505-00001",
            "title": "Paper A",
            "arxiv_id": "2505.00001",
            "source_url": "https://arxiv.org/abs/2505.00001",
            "pdf_url": "https://arxiv.org/pdf/2505.00001.pdf",
            "authors": ["Ada"],
            "published_at": "2026-05-08T00:00:00Z",
            "traffic_date": "2026-05-09",
            "view_rank": 1,
            "view_count": 1234,
        },
        summary=summary,
    )

    detail = json.loads((tmp_path / "2026-05-10" / "2505-00001.json").read_text(encoding="utf-8"))
    index = json.loads((tmp_path / "2026-05-10" / "index.json").read_text(encoding="utf-8"))

    assert detail["title"] == "Paper A"
    assert index[0]["view_rank"] == 1
