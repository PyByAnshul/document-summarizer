import pytest

from documents.models import Document


@pytest.mark.django_db
def test_document_default_status():
    document = Document.objects.create(
        original_filename="test.pdf",
        file_type="pdf",
        file_size=100,
    )

    assert document.status == Document.Status.PENDING


@pytest.mark.django_db
def test_document_default_values():
    document = Document.objects.create(
        original_filename="test.pdf",
        file_type="pdf",
    )

    assert document.keywords == []
    assert document.word_count == 0
    assert document.llm_response == {}
    assert document.status == Document.Status.PENDING
