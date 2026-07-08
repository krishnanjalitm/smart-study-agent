"""
smart-study-agent/backend/app/agents/summary_agent.py
Summary Agent
──────────────
Responsibility:
  Generate Short / Medium / Detailed summaries of a document using
  IBM Granite via a tailored prompt per summary length.
"""

from app.core.logger import logger
from app.db.mongo import get_db
from app.services.watsonx_client import watsonx
from app.utils.helpers import now_iso


# ── Prompt templates ──────────────────────────────────────────────────────────

_PROMPTS = {
    "short": (
        "You are an expert academic summariser. "
        "Provide a concise summary of the following text in 3-5 sentences. "
        "Capture only the most important points.\n\n"
        "Text:\n{text}\n\nShort Summary:"
    ),
    "medium": (
        "You are an expert academic summariser. "
        "Provide a comprehensive summary of the following text in 2-3 paragraphs. "
        "Cover main ideas, key concepts, and important details.\n\n"
        "Text:\n{text}\n\nSummary:"
    ),
    "detailed": (
        "You are an expert academic summariser. "
        "Provide a detailed structured summary of the following text. "
        "Use headings, bullet points, and include: Key Concepts, Main Arguments, "
        "Important Facts, and Conclusions.\n\n"
        "Text:\n{text}\n\nDetailed Summary:"
    ),
}

# Approximate token limits per length
_MAX_TOKENS = {"short": 300, "medium": 700, "detailed": 1500}


def generate_summary(document_id: str, length: str = "medium") -> dict:
    """
    Generate a summary for *document_id* at the requested *length*.

    Returns a dict with: document_id, length, content, created_at.
    """
    db  = get_db()
    doc = db.documents.find_one({"_id": document_id})
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    # Use stored raw_text preview — for large docs, this is the first 5 000 chars
    raw_text = doc.get("raw_text", "")
    if not raw_text:
        raise ValueError("Document has no extracted text")

    # Truncate to avoid exceeding model context window (≈ 4 000 tokens → ~16 000 chars)
    text_for_prompt = raw_text[:16_000]

    prompt   = _PROMPTS[length].format(text=text_for_prompt)
    summary  = watsonx.generate(prompt, max_new_tokens=_MAX_TOKENS[length], temperature=0.5)

    result = {
        "document_id": document_id,
        "length":      length,
        "content":     summary,
        "created_at":  now_iso(),
    }

    # Cache in MongoDB
    db.summaries.update_one(
        {"document_id": document_id, "length": length},
        {"$set": result},
        upsert=True,
    )

    logger.info(f"[SummaryAgent] {length} summary generated for doc {document_id}")
    return result
