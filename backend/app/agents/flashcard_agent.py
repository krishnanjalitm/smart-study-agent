"""
smart-study-agent/backend/app/agents/flashcard_agent.py
Flashcard Agent
────────────────
Responsibility:
  Parse a document and generate a set of pedagogically sound
  flashcard question-answer pairs using IBM Granite.
"""

import json
import re
from typing import List

from app.core.logger import logger
from app.db.mongo import get_db
from app.services.watsonx_client import watsonx
from app.utils.helpers import now_iso, new_id


_FLASHCARD_PROMPT = """You are an expert educator creating study flashcards.
Based on the text below, generate exactly {count} flashcards.

Rules:
- Each flashcard has a FRONT (question/term) and BACK (answer/definition).
- Optionally add a HINT if the concept is complex.
- Cover the most important concepts, definitions, and facts.
- Keep questions clear and concise.
- Answers should be complete but brief (1-3 sentences).

Text:
{text}

Return ONLY a valid JSON array in this exact format:
[
  {{"front": "...", "back": "...", "hint": "..."}},
  {{"front": "...", "back": "...", "hint": null}}
]

JSON:"""


def generate_flashcards(document_id: str, count: int = 10) -> dict:
    """
    Generate *count* flashcards for *document_id*.

    Returns: {{document_id, cards: [{{front, back, hint}}], created_at}}
    """
    db  = get_db()
    doc = db.documents.find_one({"_id": document_id})
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    raw_text = doc.get("raw_text", "")
    if not raw_text:
        raise ValueError("Document has no extracted text")

    prompt  = _FLASHCARD_PROMPT.format(
        count=count,
        text=raw_text[:12_000],
    )
    raw_out = watsonx.generate(prompt, max_new_tokens=2048, temperature=0.7)

    # ── Parse JSON from model output ──────────────────────────────────────────
    cards = _parse_flashcard_json(raw_out, count)

    result = {
        "document_id": document_id,
        "set_id":      new_id(),
        "cards":       cards,
        "created_at":  now_iso(),
    }

    db.flashcards.update_one(
        {"document_id": document_id},
        {"$set": result},
        upsert=True,
    )

    logger.info(f"[FlashcardAgent] {len(cards)} cards generated for doc {document_id}")
    return result


def _parse_flashcard_json(raw: str, expected_count: int) -> List[dict]:
    """
    Extract and validate a JSON array from the model output.
    Falls back to a partial parse if the JSON is malformed.
    """
    # Try to find a JSON array in the output
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            cards = json.loads(match.group())
            # Validate each card has front and back
            validated = []
            for card in cards:
                if isinstance(card, dict) and "front" in card and "back" in card:
                    validated.append({
                        "front": str(card["front"]),
                        "back":  str(card["back"]),
                        "hint":  card.get("hint"),
                    })
            if validated:
                return validated[:expected_count]
        except json.JSONDecodeError:
            pass

    # Fallback: create placeholder cards to signal the issue
    logger.warning("[FlashcardAgent] JSON parse failed; returning fallback cards")
    return [{"front": f"Card {i+1}", "back": "Please regenerate", "hint": None}
            for i in range(min(3, expected_count))]
