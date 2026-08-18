import json
import os

from litellm import completion
from litellm.exceptions import APIError
from pydantic import BaseModel, Field, ValidationError

from documents.prompts import load_prompt


class LLMServiceError(Exception):
    pass


class DocumentAnalysis(BaseModel):
    title: str = Field(description="A concise title for the document")
    summary: str = Field(description="A concise summary of the document")
    keywords: list[str] = Field(description="Important keywords from the document")
    language: str = Field(description="The primary language of the document")
    word_count: int = Field(default=0, description="Number of words in the document")


def analyze_document(document_text: str) -> DocumentAnalysis:
    if not document_text or not document_text.strip():
        raise LLMServiceError("Document text cannot be empty.")

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL_NAME") or "openrouter/poolside/laguna-s-2.1:free"

    if not api_key:
        raise LLMServiceError("OPENROUTER_API_KEY is not configured.")

    system_prompt = load_prompt("document_analysis.md")

    try:
        response = completion(
            model=model,
            api_key=api_key,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": document_text},
            ],
            temperature=0,
            timeout=30,
            num_retries=3,
            response_format={"type": "json_object"},
        )

        if not response or not response.choices:
            raise LLMServiceError("LLM returned an invalid response.")

        content = response.choices[0].message.content
        if not content:
            raise LLMServiceError("LLM returned an empty response.")

        data = json.loads(content)
        return DocumentAnalysis.model_validate(
            {**data, "word_count": len(document_text.split())}
        )

    except LLMServiceError:
        raise
    except (APIError, json.JSONDecodeError, ValidationError) as exc:
        raise LLMServiceError("LLM returned a malformed response.") from exc
    except Exception as exc:
        raise LLMServiceError("Unexpected error while calling the LLM provider.") from exc
