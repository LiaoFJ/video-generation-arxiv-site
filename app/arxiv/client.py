from datetime import date, timedelta
from typing import Any, Callable
from xml.etree import ElementTree as ET

import httpx

from app.arxiv.models import RankedPaper

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def build_ranking_url(category: str, traffic_date: str, template: str | None) -> str:
    if template:
        return template.format(category=category, date=traffic_date)
    return f"https://huggingface.co/papers?date={traffic_date}"


def normalize_arxiv_id(value: str) -> str:
    raw = value.rstrip("/").split("/")[-1]
    return raw.split("v", 1)[0]


def resolve_ranking_date(
    requested_date: str,
    fetch_html_for_date: Callable[[str], str],
    max_backtrack_days: int = 3,
) -> tuple[str, str]:
    current_date = date.fromisoformat(requested_date)
    for offset in range(max_backtrack_days + 1):
        candidate = (current_date - timedelta(days=offset)).isoformat()
        html = fetch_html_for_date(candidate)
        if '/papers/' in html:
            return candidate, html
    raise ValueError(f"No ranking page with papers found within {max_backtrack_days} day(s) of {requested_date}.")


def parse_arxiv_api_response(
    xml_text: str,
    ranking_lookup: dict[str, dict[str, Any]],
) -> list[RankedPaper]:
    root = ET.fromstring(xml_text)
    papers: list[RankedPaper] = []

    for entry in root.findall("atom:entry", ATOM_NS):
        arxiv_id = normalize_arxiv_id(entry.findtext("atom:id", default="", namespaces=ATOM_NS))
        if not arxiv_id or arxiv_id not in ranking_lookup:
            continue

        ranking = ranking_lookup[arxiv_id]
        title = entry.findtext("atom:title", default="", namespaces=ATOM_NS).strip()
        summary = entry.findtext("atom:summary", default="", namespaces=ATOM_NS).strip()
        published_at = entry.findtext("atom:published", default="", namespaces=ATOM_NS).strip()
        authors = [
            author.findtext("atom:name", default="", namespaces=ATOM_NS).strip()
            for author in entry.findall("atom:author", ATOM_NS)
            if author.findtext("atom:name", default="", namespaces=ATOM_NS).strip()
        ]
        categories = [
            category.attrib.get("term", "").strip()
            for category in entry.findall("atom:category", ATOM_NS)
            if category.attrib.get("term", "").strip()
        ]
        primary_category = ranking["source_category"]
        if primary_category not in categories and primary_category:
            categories.insert(0, primary_category)

        papers.append(
            RankedPaper(
                arxiv_id=arxiv_id,
                title=title,
                summary=summary,
                source_url=f"https://arxiv.org/abs/{arxiv_id}",
                pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                primary_category=primary_category,
                categories=categories,
                authors=authors,
                published_at=published_at,
                traffic_date=ranking["traffic_date"],
                view_rank=ranking["view_rank"],
                view_count=ranking["view_count"],
            )
        )

    return papers


class ArxivClient:
    def __init__(self, timeout_seconds: float = 30.0, user_agent: str = "video-generation-arxiv-site/0.1.0"):
        self._client = httpx.Client(
            timeout=timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": user_agent},
        )

    def fetch_ranking_html(self, url: str) -> str:
        response = self._client.get(url)
        response.raise_for_status()
        return response.text

    def fetch_metadata(self, ranking_lookup: dict[str, dict[str, Any]]) -> list[RankedPaper]:
        ids = ",".join(ranking_lookup)
        response = self._client.get(
            "https://export.arxiv.org/api/query",
            params={"id_list": ids, "max_results": len(ranking_lookup)},
        )
        response.raise_for_status()
        return parse_arxiv_api_response(response.text, ranking_lookup)

    def download_pdf(self, pdf_url: str) -> bytes:
        response = self._client.get(pdf_url)
        response.raise_for_status()
        return response.content
