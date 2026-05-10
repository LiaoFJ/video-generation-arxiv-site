from app.arxiv.models import RankedPaper


def is_relevant_paper(paper: RankedPaper, keywords: list[str]) -> bool:
    haystack = f"{paper.title}\n{paper.summary}".lower()
    return any(keyword.lower() in haystack for keyword in keywords)
