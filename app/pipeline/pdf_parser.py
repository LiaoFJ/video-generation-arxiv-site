import fitz


def extract_text_from_document(document) -> str:
    chunks: list[str] = []
    for page in document:
        text = page.get_text().strip()
        if text:
            chunks.append(text)
    return "\n\n".join(chunks)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        return extract_text_from_document(document)
