import io

import pytest
from docx import Document

from app.services.extraction import (
    MAX_FILE_BYTES,
    ExtractionError,
    extract_text,
)


def make_docx(paragraphs: list[str]) -> bytes:
    doc = Document()
    for p in paragraphs:
        doc.add_paragraph(p)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_docx_extraction_roundtrip():
    text = extract_text("cv.docx", make_docx(["Senior Python Developer"] * 20))
    assert "Senior Python Developer" in text


def test_unsupported_extension_rejected():
    with pytest.raises(ExtractionError, match="PDF or DOCX"):
        extract_text("cv.txt", b"some text " * 100)


def test_oversized_file_rejected():
    with pytest.raises(ExtractionError, match="5 MB"):
        extract_text("cv.pdf", b"x" * (MAX_FILE_BYTES + 1))


def test_too_little_text_rejected():
    with pytest.raises(ExtractionError, match="scanned"):
        extract_text("cv.docx", make_docx(["Hi"]))


def test_corrupt_docx_rejected():
    with pytest.raises(ExtractionError):
        extract_text("cv.docx", b"not a real docx file" * 20)
