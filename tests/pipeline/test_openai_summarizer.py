from app.pipeline.openai_summarizer import (
    OpenAIResponsesSummarizer,
    extract_chat_completion_text,
    extract_output_text,
    parse_relevance_payload,
)


def test_extract_output_text_prefers_top_level_field():
    payload = {"output_text": '{"summary_zh":"摘要"}'}

    assert extract_output_text(payload) == '{"summary_zh":"摘要"}'


def test_extract_output_text_falls_back_to_output_items():
    payload = {
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": '{"summary_zh":"摘要"}'},
                ]
            }
        ]
    }

    assert extract_output_text(payload) == '{"summary_zh":"摘要"}'


def test_extract_chat_completion_text_reads_first_choice():
    payload = {
        "choices": [
            {
                "message": {
                    "content": '{"summary_zh":"摘要"}',
                }
            }
        ]
    }

    assert extract_chat_completion_text(payload) == '{"summary_zh":"摘要"}'


def test_parse_relevance_payload_reads_is_relevant_flag():
    payload = {"is_relevant": True, "reason": "Focuses on text-to-video generation."}

    is_relevant, reason = parse_relevance_payload(payload)

    assert is_relevant is True
    assert reason == "Focuses on text-to-video generation."


def test_should_use_chat_completions_for_deepseek_provider():
    assert OpenAIResponsesSummarizer._should_use_chat_completions(
        "https://api.deepseek.com",
        "deepseek-v4-flash",
    )
