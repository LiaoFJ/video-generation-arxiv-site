import re

from app.arxiv.models import RankedPaper


def parse_ranking_html(html: str, traffic_date: str) -> list[RankedPaper]:
    matches = re.findall(
        r'/abs/([^"]+)">([^<]+)</a>.*?<span class="category">([^<]+)</span>',
        html,
        re.S,
    )
    papers: list[RankedPaper] = []

    for index, (arxiv_id, title, category) in enumerate(matches, start=1):
        category = category.strip()
        papers.append(
            RankedPaper(
                arxiv_id=arxiv_id,
                title=title.strip(),
                summary="",
                source_url=f"https://arxiv.org/abs/{arxiv_id}",
                pdf_url=f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                primary_category=category,
                categories=[category],
                authors=[],
                published_at="",
                traffic_date=traffic_date,
                view_rank=index,
                view_count=None,
            )
        )

    return papers
