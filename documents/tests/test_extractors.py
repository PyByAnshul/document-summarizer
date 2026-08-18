import pytest

from documents.services.extraction import extract_text


def test_extract_text_from_txt(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello this is a test document.", encoding="utf-8")

    result = extract_text(str(file_path))
    assert result == "Hello this is a test document."


def test_unsupported_file_type(tmp_path):
    file_path = tmp_path / "test.exe"
    file_path.write_text("invalid")

    with pytest.raises(ValueError, match="Unsupported"):
        extract_text(str(file_path))


def test_empty_document_is_rejected(tmp_path):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="empty"):
        extract_text(str(file_path))
