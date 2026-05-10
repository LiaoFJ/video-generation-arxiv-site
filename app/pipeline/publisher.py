import json
from pathlib import Path

from app.pipeline.schemas import SummaryResult
from app.storage.content_store import write_json


def publish_paper(content_root: Path, archive_date: str, paper: dict, summary: SummaryResult) -> None:
    archive_dir = content_root / archive_date
    detail_payload = {**paper, **summary.model_dump(), "archived_at": archive_date}
    detail_path = archive_dir / f"{paper['slug']}.json"
    write_json(detail_path, detail_payload)

    index_path = archive_dir / "index.json"
    if index_path.exists():
        index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    else:
        index_payload = []

    index_payload.append(
        {
            "slug": paper["slug"],
            "title": paper["title"],
            "arxiv_id": paper["arxiv_id"],
            "source_url": paper["source_url"],
            "published_at": paper["published_at"],
            "archived_at": archive_date,
            "traffic_date": paper["traffic_date"],
            "view_rank": paper["view_rank"],
            "view_count": paper["view_count"],
            "one_sentence_takeaway": summary.one_sentence_takeaway,
        }
    )
    index_payload.sort(key=lambda item: item["view_rank"])
    write_json(index_path, index_payload)
