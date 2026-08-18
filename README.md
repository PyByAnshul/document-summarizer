# Document Summarizer API

Upload a PDF, DOCX, or TXT file. Get back a summary, title, keywords, and language — processed asynchronously through an LLM.

Built with Django REST Framework, Celery, and pymupdf for extraction.

## Postman Collection

[https://www.postman.com/user-service-5414/workspace/document-summarizer/example/27034953-9fbd47f4-fe17-4445-a520-9f50c8d57d86?action=share&creator=27034953&active-environment=27034953-e01f25e2-eec6-434b-a649-2ef5b6bd4e26](https://www.postman.com/user-service-5414/workspace/document-summarizer/example/27034953-9fbd47f4-fe17-4445-a520-9f50c8d57d86?action=share&creator=27034953&active-environment=27034953-e01f25e2-eec6-434b-a649-2ef5b6bd4e26)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
redis-server  # separate terminal
python manage.py migrate
python manage.py runserver
```

Put this in your `.env`:

```
OPENROUTER_API_KEY=your-key-here
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
OPENROUTER_MODEL_NAME=openrouter/poolside/laguna-s-2.1:free
```

Needs Redis running for Celery. The Dockerfile handles that via docker-compose — see below.

## Endpoints

| Method | Path                  | What it does          |
|--------|-----------------------|-----------------------|
| POST   | /api/documents/       | Upload a document     |
| GET    | /api/documents/       | List all documents    |
| GET    | /api/documents/{id}/ | Get one document      |
| DELETE | /api/documents/{id}/ | Delete a document     |

### Upload

```bash
curl -X POST http://localhost:8000/api/documents/ \
  -F "file=@document.pdf"
```

Returns `202 Accepted` immediately. Processing happens in the background.

```json
{
  "id": 1,
  "filename": "document.pdf",
  "status": "pending"
}
```

Poll `GET /api/documents/1/` until `status` flips to `"completed"`.

### Get details

```bash
curl http://localhost:8000/api/documents/1/
```

```json
{
  "id": 1,
  "original_filename": "document.pdf",
  "file_type": ".pdf",
  "file_size": 1024,
  "title": "Analysis Results",
  "summary": "The document discusses...",
  "keywords": ["keyword1", "keyword2"],
  "language": "English",
  "word_count": 500,
  "status": "completed",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:01:00Z",
  "processed_at": "2024-01-01T00:01:00Z"
}
```

## Testing

```bash
pytest documents/tests/ -v
```

## Docker

```bash
docker-compose up --build
```

Spins up the app on `:8000` and Redis.


