from app.arxiv.client import build_ranking_url, parse_arxiv_api_response, resolve_ranking_date


def test_build_ranking_url_supports_category_and_date_tokens():
    url = build_ranking_url(
        category="cs.CV",
        traffic_date="2026-05-09",
        template="https://example.com/{category}?date={date}",
    )

    assert url == "https://example.com/cs.CV?date=2026-05-09"


def test_build_ranking_url_defaults_to_huggingface_date_query():
    url = build_ranking_url(category="cs.CV", traffic_date="2026-05-09", template=None)

    assert url == "https://huggingface.co/papers?date=2026-05-09"


def test_resolve_ranking_date_rolls_back_until_page_has_entries():
    visited = []

    def fetch_html(date_token: str) -> str:
        visited.append(date_token)
        if date_token in {"2026-05-10", "2026-05-11"}:
            return "<html><body>No papers today</body></html>"
        return '<h3><a href="/papers/2505.00001">Paper A</a></h3>'

    resolved_date, html = resolve_ranking_date("2026-05-11", fetch_html, max_backtrack_days=3)

    assert resolved_date == "2026-05-09"
    assert '2505.00001' in html
    assert visited == ["2026-05-11", "2026-05-10", "2026-05-09"]


def test_parse_arxiv_api_response_enriches_ranked_papers():
    xml_text = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/2505.00001v1</id>
        <updated>2026-05-09T00:00:00Z</updated>
        <published>2026-05-08T00:00:00Z</published>
        <title>Paper A</title>
        <summary>text-to-video generation</summary>
        <author><name>Ada</name></author>
        <category term="cs.CV" />
        <category term="cs.LG" />
      </entry>
    </feed>
    """

    papers = parse_arxiv_api_response(
        xml_text,
        ranking_lookup={
            "2505.00001": {
                "traffic_date": "2026-05-09",
                "view_rank": 1,
                "view_count": 42,
                "source_category": "cs.CV",
            }
        },
    )

    assert len(papers) == 1
    assert papers[0].arxiv_id == "2505.00001"
    assert papers[0].authors == ["Ada"]
    assert papers[0].categories == ["cs.CV", "cs.LG"]
    assert papers[0].view_rank == 1
