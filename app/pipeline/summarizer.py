from app.pipeline.schemas import SummaryResult


def validate_summary_payload(payload: dict) -> SummaryResult:
    return SummaryResult.model_validate(payload)
