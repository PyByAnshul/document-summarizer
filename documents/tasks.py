from celery import shared_task
from django.utils import timezone

from .models import Document
from .services.extraction import extract_text
from .services.llms import analyze_document


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id):
    try:
        document = Document.objects.get(id=document_id)

        document.status = Document.Status.PROCESSING
        document.error_message = ""
        document.save(update_fields=["status", "error_message"])

        extracted_text = extract_text(document.file.path)
        if not extracted_text.strip():
            raise ValueError("Document contains no extractable text.")

        result = analyze_document(extracted_text)
        data = result.model_dump()

        document.extracted_text = extracted_text
        document.title = data["title"]
        document.summary = data["summary"]
        document.keywords = data["keywords"]
        document.language = data["language"]
        document.word_count = len(extracted_text.split())
        document.llm_response = data
        document.status = Document.Status.COMPLETED
        document.processed_at = timezone.now()
        document.save(update_fields=[
            "extracted_text", "title", "summary", "keywords",
            "language", "word_count", "llm_response", "status", "processed_at",
        ])

    except Document.DoesNotExist:
        return
    except Exception as exc:
        document.status = Document.Status.FAILED
        document.error_message = str(exc)
        document.save(update_fields=["status", "error_message"])
        raise self.retry(exc=exc, countdown=30)
