from app.pipeline.schemas import SummaryResult
from app.pipeline.summarizer import validate_summary_payload


def test_validate_summary_payload_requires_all_fields():
    payload = {
        "summary_zh": "这篇论文提出了一个视频生成方法。",
        "one_sentence_takeaway": "方法提高了视频一致性。",
        "method_highlights": ["扩散骨干", "时序建模"],
        "applications": ["视频创作"],
        "limitations": ["推理速度较慢"],
    }

    result = validate_summary_payload(payload)

    assert isinstance(result, SummaryResult)
    assert result.one_sentence_takeaway == "方法提高了视频一致性。"
