from pydantic import BaseModel


class RankedPaper(BaseModel):
    arxiv_id: str
    title: str
    summary: str
    source_url: str
    pdf_url: str
    primary_category: str
    categories: list[str]
    authors: list[str]
    published_at: str
    traffic_date: str
    view_rank: int
    view_count: int | None = None
