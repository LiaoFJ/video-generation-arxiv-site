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


def extract_chat_completion_text(payload: dict) -> str:
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("Chat completion response did not contain choices")

    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content

    if isinstance(content, list):
        for item in content:
            if item.get("type") == "text" and item.get("text"):
                return item["text"]

    raise ValueError("Chat completion response did not contain message content")


def parse_relevance_payload(payload: dict) -> tuple[bool, str]:
    return bool(payload.get("is_relevant")), str(payload.get("reason", "")).strip()


class OpenAIResponsesSummarizer:
    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: float = 120.0,
    ):
        self._model = model
        normalized_base_url = base_url.rstrip("/")
        self._mode = "chat_completions" if self._should_use_chat_completions(normalized_base_url, model) else "responses"
        self._client = httpx.Client(
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            base_url=normalized_base_url,
        )

    def summarize_paper(self, paper: RankedPaper, pdf_text: str):
        payload = self._create_json_response(
            system_text=(
                "你是一名科研编辑。请阅读用户提供的论文信息，并只输出 JSON。"
                "JSON 必须包含 summary_zh、one_sentence_takeaway、"
                "method_highlights、applications、limitations 这五个字段。"
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
                "仅做视频理解、视频检索、奖励建模、分析或分类的论文不算。"
            ),
        )
        return parse_relevance_payload(payload)

    @staticmethod
    def _should_use_chat_completions(base_url: str, model: str) -> bool:
        return "deepseek" in base_url.lower() or model.lower().startswith("deepseek")

    def _create_json_response(self, system_text: str, user_text: str) -> dict:
        if self._mode == "chat_completions":
            response = self._client.post(
                "/chat/completions",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system_text},
                        {"role": "user", "content": user_text},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
        else:
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
        payload = response.json()
        response_text = extract_chat_completion_text(payload) if self._mode == "chat_completions" else extract_output_text(payload)
        return json.loads(response_text)

    def _build_summary_prompt(self, paper: RankedPaper, pdf_text: str) -> str:
        truncated_text = pdf_text[:40000]
        return (
            "请根据以下论文内容生成结构化中文整理，并仅输出 json 对象。\n"
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
            "请只输出 JSON 对象。"
        )
