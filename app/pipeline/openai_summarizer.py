import json

import httpx

from app.arxiv.models import RankedPaper
from app.pipeline.summarizer import validate_summary_payload


def extract_output_text(payload: dict) -> str:
    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text

    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                return content["text"]

    raise ValueError("OpenAI response did not contain output text")


class OpenAIResponsesSummarizer:
    def __init__(self, api_key: str, model: str, base_url: str = "https://api.openai.com/v1", timeout_seconds: float = 120.0):
        self._model = model
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            base_url=base_url.rstrip("/"),
        )

    def summarize_paper(self, paper: RankedPaper, pdf_text: str):
        prompt = self._build_prompt(paper, pdf_text)
        response = self._client.post(
            "/responses",
            json={
                "model": self._model,
                "input": [
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "你是一名科研编辑。请阅读用户提供的论文信息，并只输出 JSON。"
                                    "JSON 必须包含 summary_zh, one_sentence_takeaway, "
                                    "method_highlights, applications, limitations 这五个字段。"
                                ),
                            }
                        ],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    },
                ],
                "text": {"format": {"type": "json_object"}},
            },
        )
        response.raise_for_status()
        payload = json.loads(extract_output_text(response.json()))
        return validate_summary_payload(payload)

    def _build_prompt(self, paper: RankedPaper, pdf_text: str) -> str:
        truncated_text = pdf_text[:40000]
        return (
            f"请根据以下论文内容生成结构化中文整理。\n"
            f"标题: {paper.title}\n"
            f"arXiv ID: {paper.arxiv_id}\n"
            f"分类: {', '.join(paper.categories)}\n"
            f"作者: {', '.join(paper.authors)}\n"
            f"摘要: {paper.summary}\n\n"
            f"论文正文节选:\n{truncated_text}\n\n"
            "输出要求:\n"
            "1. summary_zh: 2-4 句中文摘要\n"
            "2. one_sentence_takeaway: 1 句中文结论\n"
            "3. method_highlights: 2-4 条中文要点数组\n"
            "4. applications: 1-3 条潜在应用数组\n"
            "5. limitations: 1-3 条局限性数组\n"
            "请仅输出 JSON 对象。"
        )
