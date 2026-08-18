from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from documents.models import Document


@pytest.mark.django_db
@patch("documents.views.process_document.delay")
def test_upload_starts_processing(mock_task):
    client = APIClient()
    file = SimpleUploadedFile("test.txt", b"Hello document", content_type="text/plain")

    response = client.post("/api/documents/", {"file": file}, format="multipart")

    assert response.status_code == 202

    document = Document.objects.first()
    assert document is not None
    mock_task.assert_called_once_with(document.id)


@pytest.mark.django_db
@patch("documents.views.process_document.delay")
def test_upload_document(mock_task):
    client = APIClient()
    file = SimpleUploadedFile(
        "test.txt", b"Hello, this is a document.", content_type="text/plain"
    )

    response = client.post("/api/documents/", {"file": file}, format="multipart")

    assert response.status_code == 202
    assert Document.objects.count() == 1

    document = Document.objects.first()
    assert document.original_filename == "test.txt"
    assert document.file_type == ".txt"
    assert document.file_size == len(b"Hello, this is a document.")
    assert document.status == Document.Status.PENDING


@pytest.mark.django_db
def test_get_document():
    document = Document.objects.create(
        original_filename="report.pdf",
        file_type=".pdf",
        file_size=1000,
        title="Test Report",
        summary="Test summary",
        keywords=["test", "report"],
        language="English",
        word_count=100,
        status=Document.Status.COMPLETED,
    )

    client = APIClient()
    response = client.get(f"/api/documents/{document.id}/")

    assert response.status_code == 200
    assert response.data["id"] == document.id
    assert response.data["title"] == "Test Report"
    assert response.data["status"] == "completed"
    assert response.data["keywords"] == ["test", "report"]


@pytest.mark.django_db
def test_upload_invalid_file():
    client = APIClient()
    file = SimpleUploadedFile(
        "malware.exe", b"invalid content", content_type="application/octet-stream"
    )

    response = client.post("/api/documents/", {"file": file}, format="multipart")

    assert response.status_code == 400
    assert "file" in response.data


@pytest.mark.django_db
def test_upload_empty_file():
    client = APIClient()
    file = SimpleUploadedFile("empty.txt", b"", content_type="text/plain")

    response = client.post("/api/documents/", {"file": file}, format="multipart")

    assert response.status_code == 400
    assert "file" in response.data
