"""
smart-study-agent/backend/app/agents/quiz_agent.py
Quiz Generator Agent
─────────────────────
Responsibility:
  Generate MCQ, True/False, and Short-Answer questions from a document
  using IBM Granite, and evaluate submitted quiz answers.
"""

import json
import re
import uuid
from typing import List, Dict

from app.core.logger import logger
from app.db.mongo import get_db
from app.services.watsonx_client import watsonx
from app.utils.helpers import now_iso, new_id


# ── Prompt templates ──────────────────────────────────────────────────────────

_MCQ_PROMPT = """You are an expert exam paper setter. Based on the text below, create exactly {count} multiple-choice questions.

Rules:
- Each question must have exactly 4 options (A, B, C, D).
- Provide the correct answer letter and a brief explanation.
- Questions should test understanding, not just recall.
- Vary difficulty: mix easy, medium, and hard questions.

Text:
{text}

Return ONLY a valid JSON array:
[
  {{
    "question": "...",
    "type": "mcq",
    "options": [{{"label": "A", "text": "..."}}, {{"label": "B", "text": "..."}}, {{"label": "C", "text": "..."}}, {{"label": "D", "text": "..."}}],
    "answer": "A",
    "explanation": "..."
  }}
]

JSON:"""

_TF_PROMPT = """You are an expert exam paper setter. Based on the text below, create exactly {count} True/False questions.

Rules:
- Each statement should be unambiguous.
- Half should be True, half False.
- Provide an explanation for the correct answer.

Text:
{text}

Return ONLY a valid JSON array:
[
  {{
    "question": "...",
    "type": "true_false",
    "options": [{{"label": "True", "text": "True"}}, {{"label": "False", "text": "False"}}],
    "answer": "True",
    "explanation": "..."
  }}
]

JSON:"""

_SA_PROMPT = """You are an expert exam paper setter. Based on the text below, create exactly {count} short-answer questions.

Rules:
- Questions should require 2-4 sentence answers.
- Focus on key concepts and definitions.
- Provide a model answer.

Text:
{text}

Return ONLY a valid JSON array:
[
  {{
    "question": "...",
    "type": "short_answer",
    "options": null,
    "answer": "Model answer here...",
    "explanation": null
  }}
]

JSON:"""

_PROMPTS = {"mcq": _MCQ_PROMPT, "true_false": _TF_PROMPT, "short_answer": _SA_PROMPT}


def generate_quiz(
    document_id: str,
    question_types: List[str] = None,
    count: int = 10,
) -> dict:
    """
    Generate a mixed quiz for *document_id*.

    Returns: {{document_id, quiz_id, questions, created_at}}
    """
    question_types = question_types or ["mcq"]
    db  = get_db()
    doc = db.documents.find_one({"_id": document_id})
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    raw_text = doc.get("raw_text", "")
    if not raw_text:
        raise ValueError("Document has no extracted text")

    text_snippet = raw_text[:12_000]

    # Distribute count evenly across requested types
    per_type    = max(1, count // len(question_types))
    all_questions: List[dict] = []

    for qtype in question_types:
        prompt    = _PROMPTS[qtype].format(count=per_type, text=text_snippet)
        raw_out   = watsonx.generate(prompt, max_new_tokens=2048, temperature=0.6)
        questions = _parse_quiz_json(raw_out, qtype)
        all_questions.extend(questions[:per_type])

    # Assign unique IDs
    for q in all_questions:
        q["id"] = new_id()

    quiz_id = new_id()
    result  = {
        "document_id": document_id,
        "quiz_id":     quiz_id,
        "questions":   all_questions,
        "created_at":  now_iso(),
    }

    db.quizzes.insert_one({"_id": quiz_id, **result})
    logger.info(f"[QuizAgent] {len(all_questions)} questions generated for doc {document_id}")
    return result


def evaluate_quiz(quiz_id: str, answers: Dict[str, str]) -> dict:
    """
    Compare submitted answers against stored correct answers.

    Args:
        quiz_id: The stored quiz identifier.
        answers: {{question_id: submitted_answer}}

    Returns:
        {{quiz_id, score, total, correct, feedback}}
    """
    db   = get_db()
    quiz = db.quizzes.find_one({"_id": quiz_id})
    if not quiz:
        raise ValueError(f"Quiz {quiz_id} not found")

    questions  = quiz.get("questions", [])
    feedback   = []
    correct    = 0

    for q in questions:
        q_id       = q["id"]
        submitted  = answers.get(q_id, "").strip().lower()
        correct_ans = q["answer"].strip().lower()
        is_correct  = submitted == correct_ans

        if is_correct:
            correct += 1

        feedback.append({
            "question_id":     q_id,
            "question":        q["question"],
            "submitted":       answers.get(q_id, ""),
            "correct_answer":  q["answer"],
            "is_correct":      is_correct,
            "explanation":     q.get("explanation", ""),
        })

    total = len(questions)
    score = round((correct / total) * 100, 1) if total else 0

    logger.info(f"[QuizAgent] Quiz {quiz_id} evaluated: {correct}/{total} correct")
    return {
        "quiz_id":  quiz_id,
        "score":    score,
        "total":    total,
        "correct":  correct,
        "feedback": feedback,
    }


def _parse_quiz_json(raw: str, qtype: str) -> List[dict]:
    """Extract and validate quiz JSON from model output."""
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            questions = json.loads(match.group())
            validated = []
            for q in questions:
                if isinstance(q, dict) and "question" in q and "answer" in q:
                    validated.append({
                        "question":    q["question"],
                        "type":        qtype,
                        "options":     q.get("options"),
                        "answer":      q["answer"],
                        "explanation": q.get("explanation"),
                    })
            return validated
        except json.JSONDecodeError:
            pass
    logger.warning(f"[QuizAgent] JSON parse failed for type={qtype}")
    return []
