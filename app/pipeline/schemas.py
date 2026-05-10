from pydantic import BaseModel


class SummaryResult(BaseModel):
    summary_zh: str
    one_sentence_takeaway: str
    method_highlights: list[str]
    applications: list[str]
    limitations: list[str]
