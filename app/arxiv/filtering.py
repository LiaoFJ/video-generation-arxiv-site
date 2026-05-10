from app.arxiv.models import RankedPaper


def is_relevant_paper(paper: RankedPaper, keywords: list[str]) -> bool:
    haystack = f"{paper.title}\n{paper.summary}".lower()
    normalized_keywords = [keyword.strip().lower() for keyword in keywords if keyword and keyword.strip()]
    return any(keyword in haystack for keyword in normalized_keywords)
