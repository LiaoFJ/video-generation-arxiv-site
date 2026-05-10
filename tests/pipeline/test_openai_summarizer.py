from app.pipeline.openai_summarizer import extract_output_text


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
