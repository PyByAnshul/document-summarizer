from pathlib import Path

from rest_framework import serializers

from .models import Document


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["file"]  # noqa: RUF012

    def validate_file(self, file):
        ext = Path(file.name).suffix.lower()
        if ext not in {".pdf", ".docx", ".txt"}:
            raise serializers.ValidationError(
                "Only PDF, DOCX and TXT files are supported."
            )
        if file.size == 0:
            raise serializers.ValidationError("The uploaded file is empty.")
        return file

    def create(self, validated_data):
        file_obj = validated_data["file"]
        return Document.objects.create(
            file=file_obj,
            original_filename=file_obj.name,
            file_type=Path(file_obj.name).suffix.lower(),
            file_size=file_obj.size,
        )


class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [  # noqa: RUF012
            "id",
            "original_filename",
            "file_type",
            "file_size",
            "title",
            "status",
            "created_at",
        ]


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [  # noqa: RUF012
            "id",
            "file",
            "original_filename",
            "file_type",
            "file_size",
            "title",
            "summary",
            "keywords",
            "language",
            "word_count",
            "status",
            "error_message",
            "created_at",
            "updated_at",
            "processed_at",
        ]
