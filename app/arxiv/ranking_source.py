import re

from app.arxiv.models import RankedPaper


def parse_ranking_html(html: str, traffic_date: str) -> list[RankedPaper]:
    papers: list[RankedPaper] = []

    li_matches = re.finditer(r"<li\b[^>]*>(.*?)</li>", html, re.I | re.S)
    for index, li_match in enumerate(li_matches, start=1):
        li_html = li_match.group(1)
        link_match = re.search(
            r'<a\b[^>]*href\s*=\s*["\']/abs/([^"\'>]+)["\'][^>]*>\s*([^<]+?)\s*</a>',
            li_html,
            re.I | re.S,
        )
        category_match = re.search(
            r'<span\b[^>]*class\s*=\s*["\'][^"\']*\bcategory\b[^"\']*["\'][^>]*>\s*([^<]+?)\s*</span>',
            li_html,
            re.I | re.S,
        )
        if not link_match or not category_match:
            continue

        arxiv_id, title = link_match.group(1), link_match.group(2)
        category = category_match.group(1).strip()
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
