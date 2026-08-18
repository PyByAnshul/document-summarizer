import pytest
from pydantic import ValidationError

from documents.services.llms import DocumentAnalysis


def test_document_analysis_schema():
    result = DocumentAnalysis(
        title="Test Document",
        summary="This is a test.",
        keywords=["test"],
        language="English",
    )

    assert result.title == "Test Document"
    assert result.summary == "This is a test."
    assert result.keywords == ["test"]
    assert result.language == "English"


def test_document_analysis_invalid_data():
    with pytest.raises(ValidationError):
        DocumentAnalysis(
            title="Test",
            summary="Summary",
            keywords="not-a-list",
            language="English",
        )
