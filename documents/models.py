from django.db import models


class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    file = models.FileField(upload_to="documents/")
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)
    file_size = models.PositiveBigIntegerField(null=True)

    extracted_text = models.TextField(blank=True)

    title = models.CharField(max_length=500, blank=True)
    summary = models.TextField(blank=True)
    keywords = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=50, blank=True)
    word_count = models.PositiveIntegerField(default=0)

    llm_response = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.original_filename
