import json

from app.arxiv.models import RankedPaper
from app.cli import build_publish_plan, collect_ranked_papers, run_daily_job, run_live_daily_job
from app.config import Settings
from app.pipeline.schemas import SummaryResult


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


def test_collect_ranked_papers_filters_and_dedupes():
    html = """
    <h3><a href="/papers/2505.00001">Paper A</a></h3>
    """
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2505.00001v1</id>
        <published>2026-05-08T00:00:00Z</published>
        <title>Paper A</title>
        <summary>text-to-video generation</summary>
        <author><name>Ada</name></author>
        <category term="cs.CV" />
      </entry>
    </feed>
    """

    class FakeClient:
        def __init__(self):
            self.ranking_urls = []

        def fetch_ranking_html(self, url: str) -> str:
            self.ranking_urls.append(url)
            return html

        def fetch_metadata(self, ranking_lookup):
            from app.arxiv.client import parse_arxiv_api_response

            return parse_arxiv_api_response(xml_text, ranking_lookup)

    settings = Settings(
        CONTENT_ROOT="content",
    )

    papers = collect_ranked_papers(
        settings,
        FakeClient(),
        "2026-05-09",
        relevance_checker=lambda paper: True,
        logger=lambda message: None,
    )

    assert len(papers) == 1
    assert papers[0].arxiv_id == "2505.00001"


def test_collect_ranked_papers_does_not_filter_by_category():
    html = """
    <h3><a href="/papers/2505.00009">Paper X</a></h3>
    """
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2505.00009v1</id>
        <published>2026-05-08T00:00:00Z</published>
        <title>Paper X</title>
        <summary>text-to-video generation</summary>
        <author><name>Ada</name></author>
        <category term="stat.ML" />
      </entry>
    </feed>
    """

    class FakeClient:
        def fetch_ranking_html(self, url: str) -> str:
            return html

        def fetch_metadata(self, ranking_lookup):
            from app.arxiv.client import parse_arxiv_api_response

            return parse_arxiv_api_response(xml_text, ranking_lookup)

    papers = collect_ranked_papers(
        Settings(CONTENT_ROOT="content"),
        FakeClient(),
        "2026-05-09",
        relevance_checker=lambda paper: True,
        logger=lambda message: None,
    )

    assert len(papers) == 1
    assert papers[0].categories == ["stat.ML"]


def test_collect_ranked_papers_uses_model_relevance_checker_for_candidates():
    html = """
    <h3><a href="/papers/2505.00011">Paper Good</a></h3>
    <h3><a href="/papers/2505.00012">Paper Bad</a></h3>
    """
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2505.00011v1</id>
        <published>2026-05-08T00:00:00Z</published>
        <title>Video Planning Paper</title>
        <summary>video reasoning with generation components</summary>
        <author><name>Ada</name></author>
        <category term="cs.CV" />
      </entry>
      <entry>
        <id>http://arxiv.org/abs/2505.00012v1</id>
        <published>2026-05-08T00:00:00Z</published>
        <title>Video Analytics Paper</title>
        <summary>video analytics and tracking</summary>
        <author><name>Bob</name></author>
        <category term="cs.CV" />
      </entry>
    </feed>
    """

    class FakeClient:
        def fetch_ranking_html(self, url: str) -> str:
            return html

        def fetch_metadata(self, ranking_lookup):
            from app.arxiv.client import parse_arxiv_api_response

            return parse_arxiv_api_response(xml_text, ranking_lookup)

    calls = []

    def checker(paper):
        calls.append(paper.arxiv_id)
        return paper.arxiv_id == "2505.00011"

    papers = collect_ranked_papers(
        Settings(CONTENT_ROOT="content", keywords=["video"]),
        FakeClient(),
        "2026-05-09",
        relevance_checker=checker,
        logger=lambda message: None,
    )

    assert [paper.arxiv_id for paper in papers] == ["2505.00011"]
    assert calls == ["2505.00011", "2505.00012"]


def test_run_live_daily_job_writes_content(tmp_path):
    paper = RankedPaper(
        arxiv_id="2505.00001",
        title="Paper A",
        summary="text-to-video generation",
        source_url="https://arxiv.org/abs/2505.00001",
        pdf_url="https://arxiv.org/pdf/2505.00001.pdf",
        primary_category="cs.CV",
        categories=["cs.CV"],
        authors=["Ada"],
        published_at="2026-05-08T00:00:00Z",
        traffic_date="2026-05-09",
        view_rank=1,
        view_count=100,
    )

    class FakeClient:
        def fetch_ranking_html(self, url: str) -> str:
            return '<h3><a href="/papers/2505.00001">Paper A</a></h3>'

        def fetch_metadata(self, ranking_lookup):
            return [paper]

        def download_pdf(self, pdf_url: str) -> bytes:
            return b"%PDF-1.4 fake"

    class FakeSummarizer:
        def is_video_generation_paper(self, paper):
            return True, "test stub"

        def summarize_paper(self, paper, pdf_text: str):
            return SummaryResult(
                summary_zh="中文摘要",
                one_sentence_takeaway="一句话结论",
                method_highlights=["亮点"],
                applications=["应用"],
                limitations=["局限"],
            )

    settings = Settings(
        CONTENT_ROOT=str(tmp_path),
        OPENAI_API_KEY="test-key",
    )

    count = run_live_daily_job(
        settings=settings,
        arxiv_client=FakeClient(),
        summarizer=FakeSummarizer(),
        archive_date="2026-05-10",
        traffic_date="2026-05-09",
        pdf_text_extractor=lambda _: "fake pdf text",
    )

    detail = json.loads((tmp_path / "2026-05-10" / "2505-00001.json").read_text(encoding="utf-8"))
    assert count == 1
    assert detail["summary_zh"] == "中文摘要"
