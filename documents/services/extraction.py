from pathlib import Path

import pymupdf as fitz
from docx import Document as DocxDocument


class DocumentExtractionError(Exception):
    pass


def extract_from_pdf(file_path):
    try:
        with fitz.open(file_path) as pdf:
            return "\n".join(page.get_text() for page in pdf)
    except Exception as exc:
        raise DocumentExtractionError("Failed to extract text from PDF.") from exc


def extract_from_docx(file_path):
    try:
        document = DocxDocument(file_path)
        return "\n".join(p.text for p in document.paragraphs if p.text.strip())
    except Exception as exc:
        raise DocumentExtractionError("Failed to extract text from DOCX.") from exc


def extract_from_txt(file_path):
    with open(file_path, encoding="utf-8") as file:
        return file.read()


def extract_text(file_path):
    extension = Path(file_path).suffix.lower()

    extractors = {
        ".pdf": extract_from_pdf,
        ".docx": extract_from_docx,
        ".txt": extract_from_txt,
    }

    if extension not in extractors:
        raise ValueError(
            "Unsupported file type. Only PDF, DOCX and TXT files are supported."
        )

    text = extractors[extension](file_path)

    if not text.strip():
        raise ValueError("Document text is empty.")

    return text
