"""
RAG STEP 1: Parsing.

Turns an uploaded file (PDF / DOCX / TXT) into a list of "pages" of raw
text, each tagged with its page number. Keeping page numbers here — as
early as possible in the pipeline — is what lets us cite "Document X,
page 4" at the very end, instead of just "somewhere in Document X".

For .txt and .docx files there's no native concept of a "page", so we
treat the whole document as a single page (page_number=None) rather than
inventing a fake page count.
"""
from dataclasses import dataclass
from io import BytesIO

from pypdf import PdfReader
from docx import Document as DocxDocument


@dataclass
class ParsedPage:
    page_number: int | None  # 1-indexed; None if the format has no pages
    text: str


def parse_document(filename: str, file_bytes: bytes) -> list[ParsedPage]:
    """Dispatch to the right parser based on file extension."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _parse_pdf(file_bytes)
    elif lower.endswith(".docx"):
        return _parse_docx(file_bytes)
    elif lower.endswith(".txt"):
        return _parse_txt(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type for '{filename}'. Supported: .pdf, .docx, .txt"
        )


def _parse_pdf(file_bytes: bytes) -> list[ParsedPage]:
    reader = PdfReader(BytesIO(file_bytes))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = text.strip()
        if text:  # skip genuinely blank pages
            pages.append(ParsedPage(page_number=i, text=text))
    return pages


def _parse_docx(file_bytes: bytes) -> list[ParsedPage]:
    doc = DocxDocument(BytesIO(file_bytes))
    # python-docx has no reliable page-break concept (page breaks are a
    # rendering-time detail in Word, not stored per-paragraph), so we
    # treat the whole doc as one logical page.
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if not full_text.strip():
        return []
    return [ParsedPage(page_number=None, text=full_text)]


def _parse_txt(file_bytes: bytes) -> list[ParsedPage]:
    text = file_bytes.decode("utf-8", errors="replace").strip()
    if not text:
        return []
    return [ParsedPage(page_number=None, text=text)]
