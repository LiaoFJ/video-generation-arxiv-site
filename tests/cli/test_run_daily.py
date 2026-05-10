from app.arxiv.models import RankedPaper
from app.cli import build_publish_plan, run_daily_job


def test_build_publish_plan_limits_and_sorts_ranked_papers():
    papers = [
        RankedPaper(
            arxiv_id="2505.00002",
            title="Paper B",
            summary="image-to-video system",
            source_url="https://arxiv.org/abs/2505.00002",
            pdf_url="https://arxiv.org/pdf/2505.00002.pdf",
            primary_category="cs.CV",
            categories=["cs.CV"],
            authors=["B"],
            published_at="2026-05-08T00:00:00Z",
            traffic_date="2026-05-09",
            view_rank=2,
            view_count=None,
        ),
        RankedPaper(
            arxiv_id="2505.00001",
            title="Paper A",
            summary="text-to-video system",
            source_url="https://arxiv.org/abs/2505.00001",
            pdf_url="https://arxiv.org/pdf/2505.00001.pdf",
            primary_category="cs.CV",
            categories=["cs.CV"],
            authors=["A"],
            published_at="2026-05-08T00:00:00Z",
            traffic_date="2026-05-09",
            view_rank=1,
            view_count=None,
        ),
    ]

    plan = build_publish_plan(papers, limit=1)

    assert [paper.arxiv_id for paper in plan] == ["2505.00001"]


def test_run_daily_job_publishes_only_limited_papers():
    published = []
    papers = [
        RankedPaper(
            arxiv_id="2505.00001",
            title="Paper A",
            summary="text-to-video system",
            source_url="https://arxiv.org/abs/2505.00001",
            pdf_url="https://arxiv.org/pdf/2505.00001.pdf",
            primary_category="cs.CV",
            categories=["cs.CV"],
            authors=["A"],
            published_at="2026-05-08T00:00:00Z",
            traffic_date="2026-05-09",
            view_rank=1,
            view_count=None,
        ),
        RankedPaper(
            arxiv_id="2505.00002",
            title="Paper B",
            summary="image-to-video system",
            source_url="https://arxiv.org/abs/2505.00002",
            pdf_url="https://arxiv.org/pdf/2505.00002.pdf",
            primary_category="cs.CV",
            categories=["cs.CV"],
            authors=["B"],
            published_at="2026-05-08T00:00:00Z",
            traffic_date="2026-05-09",
            view_rank=2,
            view_count=None,
        ),
    ]

    run_daily_job(
        papers=papers,
        limit=1,
        publish_fn=lambda paper: published.append(paper.arxiv_id),
    )

    assert published == ["2505.00001"]
