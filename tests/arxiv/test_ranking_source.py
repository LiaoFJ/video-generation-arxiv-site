from app.arxiv.ranking_source import parse_ranking_html


def test_parse_ranking_html_extracts_ranked_papers():
    html = """
    <ol>
      <li>
        <a href="/abs/2505.00001">Paper A</a>
        <span class="category">cs.CV</span>
      </li>
      <li>
        <a href="/abs/2505.00002">Paper B</a>
        <span class="category">cs.AI</span>
      </li>
    </ol>
    """

    papers = parse_ranking_html(html, traffic_date="2026-05-09")

    assert papers[0].arxiv_id == "2505.00001"
    assert papers[0].view_rank == 1
    assert papers[1].primary_category == "cs.AI"


def test_parse_ranking_html_accepts_common_html_variants():
    html = """
    <ol>
      <li>
        <a class="title" href="/abs/2505.00003">Paper C</a>
        <span class="category primary">cs.LG</span>
      </li>
    </ol>
    """

    papers = parse_ranking_html(html, traffic_date="2026-05-09")

    assert len(papers) == 1
    assert papers[0].arxiv_id == "2505.00003"
    assert papers[0].primary_category == "cs.LG"
