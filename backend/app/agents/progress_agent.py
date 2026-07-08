"""
smart-study-agent/backend/app/agents/progress_agent.py
Progress Analysis Agent
────────────────────────
Responsibility:
  Aggregate study activity, compute analytics, and generate
  AI-driven insights about the student's learning progress.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from collections import defaultdict

from app.core.logger import logger
from app.db.mongo import get_db
from app.services.watsonx_client import watsonx
from app.utils.helpers import now_iso


_INSIGHT_PROMPT = """You are a learning analytics expert and study coach.

Based on the student's study data below, provide 3-5 actionable insights and recommendations.

Study Data:
- Total study sessions: {total_sessions}
- Average quiz score: {avg_score}%
- Documents studied: {docs_studied}
- Flashcards reviewed: {flashcards_reviewed}
- Total study time: {total_hours} hours
- Best performing topic: {best_topic}
- Lowest quiz score: {lowest_score}%
- Study streak (consecutive days): {streak} days

Provide:
1. Strengths observed
2. Areas needing improvement
3. Recommended next steps
4. Motivational message

Keep it encouraging, specific, and actionable.

Insights:"""


def log_activity(
    user_id: str,
    activity_type: str,
    details: dict,
) -> dict:
    """
    Log a study activity event.

    activity_type: 'quiz_completed' | 'flashcard_reviewed' |
                   'document_read' | 'chat_session'
    """
    db  = get_db()
    today = datetime.utcnow().strftime("%Y-%m-%d")

    update = {
        "$inc":  {},
        "$set":  {"user_id": user_id, "last_updated": now_iso()},
        "$push": {"activities": {"type": activity_type, "details": details, "ts": now_iso()}},
    }

    if activity_type == "quiz_completed":
        update["$inc"]["quiz_count"]   = 1
        update["$inc"]["total_score"]  = details.get("score", 0)
        update["$inc"]["study_minutes"] = details.get("minutes", 0)
    elif activity_type == "flashcard_reviewed":
        update["$inc"]["flashcards_reviewed"] = details.get("count", 1)
    elif activity_type == "document_read":
        update["$inc"]["documents_read"] = 1
    elif activity_type == "chat_session":
        update["$inc"]["chat_sessions"] = 1

    db.progress.update_one(
        {"user_id": user_id, "date": today},
        update,
        upsert=True,
    )
    logger.info(f"[ProgressAgent] Logged {activity_type} for user {user_id}")
    return {"status": "logged", "date": today}


def get_dashboard(user_id: str) -> dict:
    """
    Compute dashboard statistics for the given user.

    Returns aggregated metrics + AI-generated insights.
    """
    db      = get_db()
    records = list(db.progress.find({"user_id": user_id}))

    # ── Aggregate ─────────────────────────────────────────────────────────────
    total_sessions         = len(records)
    total_quiz_score       = sum(r.get("total_score", 0)   for r in records)
    total_quiz_count       = sum(r.get("quiz_count", 0)    for r in records)
    total_flashcards       = sum(r.get("flashcards_reviewed", 0) for r in records)
    total_docs             = sum(r.get("documents_read", 0) for r in records)
    total_minutes          = sum(r.get("study_minutes", 0) for r in records)

    avg_score   = round(total_quiz_score / total_quiz_count, 1) if total_quiz_count else 0
    total_hours = round(total_minutes / 60, 1)

    # Quiz score over time (last 30 days)
    quiz_trend = []
    for r in sorted(records, key=lambda x: x.get("date", ""))[-30:]:
        if r.get("quiz_count", 0) > 0:
            quiz_trend.append({
                "date":  r["date"],
                "score": round(r.get("total_score", 0) / r.get("quiz_count", 1), 1),
            })

    # Study streak
    streak = _compute_streak(records)

    # Documents studied
    doc_ids   = [r.get("document_id") for r in db.documents.find({"user_id": user_id})]
    docs_count = len(doc_ids)

    # ── AI Insights ───────────────────────────────────────────────────────────
    insight_text = ""
    if total_sessions > 0:
        try:
            scores = [
                round(r.get("total_score", 0) / r.get("quiz_count", 1), 1)
                for r in records if r.get("quiz_count", 0) > 0
            ]
            lowest = min(scores) if scores else 0
            prompt = _INSIGHT_PROMPT.format(
                total_sessions      = total_sessions,
                avg_score           = avg_score,
                docs_studied        = docs_count,
                flashcards_reviewed = total_flashcards,
                total_hours         = total_hours,
                best_topic          = "Review your highest-score quiz",
                lowest_score        = lowest,
                streak              = streak,
            )
            insight_text = watsonx.generate(prompt, max_new_tokens=600, temperature=0.6)
        except Exception as exc:
            logger.warning(f"[ProgressAgent] Insight generation failed: {exc}")

    return {
        "user_id":       user_id,
        "total_sessions": total_sessions,
        "avg_quiz_score": avg_score,
        "total_flashcards": total_flashcards,
        "total_documents":  docs_count,
        "total_study_hours": total_hours,
        "study_streak":  streak,
        "quiz_trend":    quiz_trend,
        "ai_insights":   insight_text,
    }


def _compute_streak(records: list) -> int:
    """Count consecutive study days up to today."""
    if not records:
        return 0
    dates = sorted({r.get("date", "") for r in records if r.get("date")}, reverse=True)
    if not dates:
        return 0

    streak = 0
    check  = datetime.utcnow().date()
    for d in dates:
        try:
            record_date = datetime.strptime(d, "%Y-%m-%d").date()
        except ValueError:
            continue
        if record_date == check:
            streak += 1
            check -= timedelta(days=1)
        else:
            break
    return streak
