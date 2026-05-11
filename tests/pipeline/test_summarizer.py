from app.pipeline.schemas import SummaryResult
from app.pipeline.summarizer import validate_summary_payload


def test_validate_summary_payload_requires_all_fields():
    payload = {
        "summary_zh": "这篇论文提出了一种视频生成方法。",
        "one_sentence_takeaway": "方法提高了视频一致性。",
        "problem_statement_zh": "现有方法在长视频场景下容易出现时序漂移和主体不稳定。",
        "core_design_zh": "论文通过分层时序建模和条件扩散控制来稳定生成过程。",
        "method_highlights": ["扩散骨干", "时序建模"],
        "applications": ["视频创作"],
        "limitations": ["推理速度较慢"],
    }

    result = validate_summary_payload(payload)

    assert isinstance(result, SummaryResult)
    assert result.problem_statement_zh.startswith("现有方法")
    assert result.core_design_zh.startswith("论文通过")
