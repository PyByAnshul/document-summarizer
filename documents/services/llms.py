import json
import logging
import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from litellm import completion
from litellm.exceptions import APIError
from pydantic import BaseModel, Field, ValidationError

from documents.prompts import load_prompt

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 12_000
DEFAULT_CHUNK_OVERLAP = 300


class LLMServiceError(Exception):
    pass


class DocumentAnalysis(BaseModel):
    title: str = Field(description="A concise title for the document")
    summary: str = Field(description="A concise summary of the document")
    keywords: list[str] = Field(description="Important keywords from the document")
    language: str = Field(description="The primary language of the document")
    word_count: int = Field(default=0, description="Number of words in the document")



def _chunk_text(document_text: str) -> list[str]:

    if len(document_text) <= DEFAULT_CHUNK_SIZE:
        logger.info("Document fits in one LLM chunk: characters=%d", len(document_text))
        return [document_text]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=DEFAULT_CHUNK_SIZE,
        chunk_overlap=DEFAULT_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(document_text)
    return chunks


def _complete_analysis(document_text: str, system_prompt: str) -> DocumentAnalysis:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL_NAME") or "openrouter/poolside/laguna-s-2.1:free"
    base_url = os.getenv("OPENROUTER_BASE_URL") or "https://openrouter.ai/api/v1"

    if not api_key:
        logger.error("LLM analysis cannot start: OPENROUTER_API_KEY is not configured")
        raise LLMServiceError("OPENROUTER_API_KEY is not configured.")

    try:
        response = completion(
            base_url=base_url,
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
        analysis = DocumentAnalysis.model_validate(
            {**data, "word_count": len(document_text.split())}
        )
        return analysis

    except LLMServiceError:
        raise
    except (APIError, json.JSONDecodeError, ValidationError) as exc:
        logger.error("LLM returned a malformed response: error_type=%s", type(exc).__name__)
        raise LLMServiceError("LLM returned a malformed response.") from exc
    except Exception as exc:
        logger.error("Unexpected LLM provider error: error_type=%s", type(exc).__name__)
        raise LLMServiceError("Unexpected error while calling the LLM provider.") from exc


def _analysis_text(analysis: DocumentAnalysis) -> str:
    return (
        f"Title: {analysis.title}\n"
        f"Summary: {analysis.summary}\n"
        f"Keywords: {', '.join(analysis.keywords)}\n"
        f"Language: {analysis.language}"
    )


def _merge_analyses(analyses: list[DocumentAnalysis]) -> list[DocumentAnalysis]:

    logger.info("Summary merge started: input_analyses=%d", len(analyses))
    merge_prompt = load_prompt("summary_merge.md")
    combined_summaries = "\n\n".join(
        _analysis_text(analysis) for analysis in analyses
    )

    merged_chunks = _chunk_text(combined_summaries)
    merged_analyses = [
        _complete_analysis(chunk, merge_prompt)
        for chunk in merged_chunks
    ]
    logger.info("Summary merge completed: output_analyses=%d", len(merged_analyses))
    return merged_analyses


def analyze_document(document_text: str) -> DocumentAnalysis:
    if not document_text or not document_text.strip():
        raise LLMServiceError("Document text cannot be empty.")

    original_word_count = len(document_text.split())
    logger.info(
        "Document LLM analysis started: words=%d characters=%d",
        original_word_count,
        len(document_text),
    )
    system_prompt = load_prompt("document_analysis.md")
    chunks = _chunk_text(document_text)

    analyses = [_complete_analysis(chunk, system_prompt) for chunk in chunks]

    reduction_round = 0
    while len(analyses) > 1:
        reduction_round += 1
        logger.info(
            "Document summary reduction started: round=%d analyses=%d",
            reduction_round,
            len(analyses),
        )
        merged_analyses = _merge_analyses(analyses)
        if len(merged_analyses) >= len(analyses):
            logger.error(
                "Document summary reduction made no progress: round=%d input=%d output=%d",
                reduction_round,
                len(analyses),
                len(merged_analyses),
            )
            raise LLMServiceError("Document summaries did not shrink during merging.")

        analyses = merged_analyses

    logger.info("Document LLM analysis completed: reduction_rounds=%d", reduction_round)
    return analyses[0].model_copy(update={"word_count": original_word_count})
