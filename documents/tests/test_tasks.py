from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.models import Document
from documents.services.llms import DocumentAnalysis
from documents.tasks import process_document


@pytest.mark.django_db
@patch("documents.tasks.analyze_document")
@patch("documents.tasks.extract_text")
def test_process_document(mock_extract, mock_analyze):
    document = Document.objects.create(
        original_filename="test.txt",
        file_type="txt",
        file_size=100,
        file=SimpleUploadedFile("test.txt", b"test content"),
    )

    mock_extract.return_value = "This is the document text."
    mock_analyze.return_value = DocumentAnalysis(
        title="Test Document",
        summary="A test document.",
        keywords=["test", "document"],
        language="English",
    )

    process_document(document.id)

    document.refresh_from_db()
    assert document.status == Document.Status.COMPLETED
    assert document.title == "Test Document"
    assert document.summary == "A test document."
    assert document.keywords == ["test", "document"]
    assert document.language == "English"
    assert document.word_count == 5


@pytest.mark.django_db
@patch("documents.tasks.extract_text")
def test_document_processing_failure(mock_extract):
    document = Document.objects.create(
        original_filename="test.pdf",
        file_type="pdf",
        file_size=100,
        file=SimpleUploadedFile("test.pdf", b"test content"),
    )

    mock_extract.side_effect = Exception("Unable to extract document text")

    with pytest.raises(Exception):
        process_document(document.id)

    document.refresh_from_db()
    assert document.status == Document.Status.FAILED
    assert document.error_message == "Unable to extract document text"
