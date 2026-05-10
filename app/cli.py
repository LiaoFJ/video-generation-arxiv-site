from app.arxiv.models import RankedPaper


def build_publish_plan(papers: list[RankedPaper], limit: int) -> list[RankedPaper]:
    return sorted(papers, key=lambda paper: paper.view_rank)[:limit]


def run_daily_job(papers: list[RankedPaper], limit: int, publish_fn) -> None:
    for paper in build_publish_plan(papers, limit=limit):
        publish_fn(paper)
