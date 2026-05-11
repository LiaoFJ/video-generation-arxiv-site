from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from app.arxiv.client import ArxivClient, build_ranking_url, resolve_ranking_date
from app.arxiv.filtering import is_relevant_paper
from app.arxiv.models import RankedPaper
from app.arxiv.ranking_source import parse_ranking_html
from app.config import Settings
from app.pipeline.openai_summarizer import OpenAIResponsesSummarizer
from app.pipeline.pdf_parser import extract_text_from_pdf_bytes
from app.pipeline.publisher import publish_paper


def build_publish_plan(papers: list[RankedPaper], limit: int) -> list[RankedPaper]:
    return sorted(papers, key=lambda paper: paper.view_rank)[:limit]


def run_daily_job(papers: list[RankedPaper], limit: int, publish_fn) -> None:
    for paper in build_publish_plan(papers, limit=limit):
        publish_fn(paper)


def default_traffic_date(today: date | None = None) -> str:
    current_day = today or datetime.now(UTC).date()
    return (current_day - timedelta(days=1)).isoformat()


def build_slug(arxiv_id: str) -> str:
    return arxiv_id.replace(".", "-")


def collect_ranked_papers(settings: Settings, arxiv_client: ArxivClient, traffic_date: str) -> list[RankedPaper]:
    ranking_lookup: dict[str, dict] = {}
    template = settings.ranking_url_template
    resolved_traffic_date, html = resolve_ranking_date(
        traffic_date,
        lambda candidate_date: arxiv_client.fetch_ranking_html(
            build_ranking_url(category="", traffic_date=candidate_date, template=template)
        ),
        max_backtrack_days=3,
    )
    ranked_entries = parse_ranking_html(html, traffic_date=resolved_traffic_date)
    for entry in ranked_entries:
        ranking_lookup[entry.arxiv_id] = {
            "traffic_date": entry.traffic_date,
            "view_rank": entry.view_rank,
            "view_count": entry.view_count,
            "source_category": "",
        }

    metadata_papers = arxiv_client.fetch_metadata(ranking_lookup)
    filtered_papers = [paper for paper in metadata_papers if is_relevant_paper(paper, settings.keywords)]
    return filtered_papers


def run_live_daily_job(
    settings: Settings,
    arxiv_client: ArxivClient | None = None,
    summarizer: OpenAIResponsesSummarizer | None = None,
    archive_date: str | None = None,
    traffic_date: str | None = None,
    pdf_text_extractor=extract_text_from_pdf_bytes,
) -> int:
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for summary generation.")

    client = arxiv_client or ArxivClient(timeout_seconds=settings.request_timeout_seconds)
    summarizer_client = summarizer or OpenAIResponsesSummarizer(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
        timeout_seconds=max(settings.request_timeout_seconds, 120.0),
    )
    resolved_archive_date = archive_date or datetime.now(UTC).date().isoformat()
    resolved_traffic_date = traffic_date or default_traffic_date()

    ranked_papers = collect_ranked_papers(settings, client, resolved_traffic_date)
    selected_papers = build_publish_plan(ranked_papers, settings.publish_limit)
    content_root = Path(settings.content_root)

    for paper in selected_papers:
        pdf_bytes = client.download_pdf(paper.pdf_url)
        pdf_text = pdf_text_extractor(pdf_bytes)
        summary = summarizer_client.summarize_paper(paper, pdf_text)
        publish_paper(
            content_root=content_root,
            archive_date=resolved_archive_date,
            paper={
                "slug": build_slug(paper.arxiv_id),
                "title": paper.title,
                "arxiv_id": paper.arxiv_id,
                "source_url": paper.source_url,
                "pdf_url": paper.pdf_url,
                "authors": paper.authors,
                "published_at": paper.published_at,
                "traffic_date": paper.traffic_date,
                "view_rank": paper.view_rank,
                "view_count": paper.view_count,
            },
            summary=summary,
        )

    return len(selected_papers)
