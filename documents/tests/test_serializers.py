from django.core.files.uploadedfile import SimpleUploadedFile

from documents.serializers import DocumentCreateSerializer


def test_pdf_file_is_valid():
    file = SimpleUploadedFile("test.pdf", b"dummy pdf content", content_type="application/pdf")
    serializer = DocumentCreateSerializer(data={"file": file})
    assert serializer.is_valid()


def test_invalid_file_type():
    file = SimpleUploadedFile(
        "test.exe", b"some content", content_type="application/octet-stream"
    )
    serializer = DocumentCreateSerializer(data={"file": file})

    assert not serializer.is_valid()
    assert "file" in serializer.errors


def test_empty_file_is_rejected():
    file = SimpleUploadedFile("test.pdf", b"", content_type="application/pdf")
    serializer = DocumentCreateSerializer(data={"file": file})

    assert not serializer.is_valid()
    assert "file" in serializer.errors
