from app.arxiv.filtering import is_relevant_paper
from app.arxiv.models import RankedPaper


def test_is_relevant_paper_matches_keyword_in_summary():
    paper = RankedPaper(
        arxiv_id="2505.00001",
        title="A Better Model",
        summary="We study text-to-video generation with diffusion transformers.",
        source_url="https://arxiv.org/abs/2505.00001",
        pdf_url="https://arxiv.org/pdf/2505.00001.pdf",
        primary_category="cs.CV",
        categories=["cs.CV"],
        authors=["Ada"],
        published_at="2026-05-08T00:00:00Z",
        traffic_date="2026-05-09",
        view_rank=1,
        view_count=None,
    )

    assert is_relevant_paper(paper, ["video generation", "text-to-video"]) is True


def test_is_relevant_paper_matches_keyword_in_title():
    paper = RankedPaper(
        arxiv_id="2505.00002",
        title="Text-to-Video for Everyone",
        summary="This abstract stays generic.",
        source_url="https://arxiv.org/abs/2505.00002",
        pdf_url="https://arxiv.org/pdf/2505.00002.pdf",
        primary_category="cs.CV",
        categories=["cs.CV"],
        authors=["Ada"],
        published_at="2026-05-08T00:00:00Z",
        traffic_date="2026-05-09",
        view_rank=2,
        view_count=None,
    )

    assert is_relevant_paper(paper, ["video generation", "text-to-video"]) is True


def test_is_relevant_paper_is_case_insensitive():
    paper = RankedPaper(
        arxiv_id="2505.00003",
        title="A Better Model",
        summary="We study TEXT-TO-VIDEO generation with diffusion transformers.",
        source_url="https://arxiv.org/abs/2505.00003",
        pdf_url="https://arxiv.org/pdf/2505.00003.pdf",
        primary_category="cs.CV",
        categories=["cs.CV"],
        authors=["Ada"],
        published_at="2026-05-08T00:00:00Z",
        traffic_date="2026-05-09",
        view_rank=3,
        view_count=None,
    )

    assert is_relevant_paper(paper, ["text-to-video"]) is True


def test_is_relevant_paper_ignores_blank_keywords():
    paper = RankedPaper(
        arxiv_id="2505.00004",
        title="Unrelated Paper",
        summary="No matching terms here.",
        source_url="https://arxiv.org/abs/2505.00004",
        pdf_url="https://arxiv.org/pdf/2505.00004.pdf",
        primary_category="cs.CV",
        categories=["cs.CV"],
        authors=["Ada"],
        published_at="2026-05-08T00:00:00Z",
        traffic_date="2026-05-09",
        view_rank=4,
        view_count=None,
    )

    assert is_relevant_paper(paper, ["", "   "]) is False
