from app.pipeline.pdf_parser import extract_text_from_document


class FakePage:
    def __init__(self, text: str):
        self._text = text

    def get_text(self) -> str:
        return self._text


def test_extract_text_from_document_joins_non_empty_pages():
    document = [FakePage("First page"), FakePage(""), FakePage("Second page")]

    text = extract_text_from_document(document)

    assert text == "First page\n\nSecond page"
