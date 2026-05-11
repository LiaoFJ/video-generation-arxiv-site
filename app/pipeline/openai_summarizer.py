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


def parse_relevance_payload(payload: dict) -> tuple[bool, str]:
    return bool(payload.get("is_relevant")), str(payload.get("reason", "")).strip()


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
        payload = self._create_json_response(
            system_text=(
                "你是一名科研编辑。请阅读用户提供的论文信息，并只输出 JSON。"
                "JSON 必须包含 summary_zh, one_sentence_takeaway, "
                "method_highlights, applications, limitations 这五个字段。"
            ),
            user_text=self._build_summary_prompt(paper, pdf_text),
        )
        return validate_summary_payload(payload)

    def is_video_generation_paper(self, paper: RankedPaper) -> tuple[bool, str]:
        payload = self._create_json_response(
            system_text=(
                "你是一名论文筛选助手。请判断一篇论文是否属于 video generation 相关工作。"
                "只输出 JSON，字段为 is_relevant(bool) 和 reason(string)。"
            ),
            user_text=(
                f"标题: {paper.title}\n"
                f"摘要: {paper.summary}\n"
                f"分类: {', '.join(paper.categories)}\n\n"
                "判断标准：与 text-to-video、image-to-video、video diffusion、video synthesis、"
                "video editing、video generation model 明确相关的论文算相关；"
                "仅仅做视频理解、视频检索、奖励建模、分析或分类的论文不算。"
            ),
        )
        return parse_relevance_payload(payload)

    def _create_json_response(self, system_text: str, user_text: str) -> dict:
        response = self._client.post(
            "/responses",
            json={
                "model": self._model,
                "input": [
                    {
                        "role": "system",
                        "content": [{"type": "input_text", "text": system_text}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": user_text}],
                    },
                ],
                "text": {"format": {"type": "json_object"}},
            },
        )
        response.raise_for_status()
        return json.loads(extract_output_text(response.json()))

    def _build_summary_prompt(self, paper: RankedPaper, pdf_text: str) -> str:
        truncated_text = pdf_text[:40000]
        return (
            "请根据以下论文内容生成结构化中文整理。\n"
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
