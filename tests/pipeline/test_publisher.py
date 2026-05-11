import json

from app.pipeline.publisher import publish_paper
from app.pipeline.schemas import SummaryResult


def test_publish_paper_writes_index_and_detail(tmp_path):
    summary = SummaryResult(
        summary_zh="中文摘要",
        one_sentence_takeaway="一句话结论",
        problem_statement_zh="现有视频生成方法在时序一致性上存在明显问题。",
        core_design_zh="论文通过显式的时序模块和条件控制来稳定生成过程。",
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
    assert detail["problem_statement_zh"].startswith("现有视频生成方法")
    assert detail["core_design_zh"].startswith("论文通过")
    assert index[0]["view_rank"] == 1


def test_publish_paper_replaces_existing_index_entry_for_same_slug(tmp_path):
    paper = {
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
    }
    first_summary = SummaryResult(
        summary_zh="第一版摘要",
        one_sentence_takeaway="第一版结论",
        problem_statement_zh="第一版痛点",
        core_design_zh="第一版设计",
        method_highlights=["亮点 A"],
        applications=["应用 A"],
        limitations=["局限 A"],
    )
    second_summary = SummaryResult(
        summary_zh="第二版摘要",
        one_sentence_takeaway="第二版结论",
        problem_statement_zh="第二版痛点",
        core_design_zh="第二版设计",
        method_highlights=["亮点 B"],
        applications=["应用 B"],
        limitations=["局限 B"],
    )

    publish_paper(content_root=tmp_path, archive_date="2026-05-10", paper=paper, summary=first_summary)
    publish_paper(content_root=tmp_path, archive_date="2026-05-10", paper=paper, summary=second_summary)

    detail = json.loads((tmp_path / "2026-05-10" / "2505-00001.json").read_text(encoding="utf-8"))
    index = json.loads((tmp_path / "2026-05-10" / "index.json").read_text(encoding="utf-8"))

    assert detail["summary_zh"] == "第二版摘要"
    assert len(index) == 1
    assert index[0]["one_sentence_takeaway"] == "第二版结论"
