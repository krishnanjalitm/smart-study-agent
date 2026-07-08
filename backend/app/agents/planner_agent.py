"""
smart-study-agent/backend/app/agents/planner_agent.py
Study Planner Agent
────────────────────
Responsibility:
  Build a personalised day-by-day study schedule based on:
    - Selected documents (topics/subjects)
    - Exam date
    - Available hours per day
    - Weak topics identified from quiz history
"""

import json
import re
from datetime import datetime, date, timedelta
from typing import List, Optional

from app.core.logger import logger
from app.db.mongo import get_db
from app.services.watsonx_client import watsonx
from app.utils.helpers import now_iso, new_id


_PLANNER_PROMPT = """You are an expert academic study coach.

A student needs a personalised study plan with the following details:
- Subjects/Documents: {subjects}
- Days until exam: {days_left}
- Study hours available per day: {hours_per_day}
- Weak topics needing extra attention: {weak_topics}

Create a day-by-day study schedule covering all subjects.
Allocate more time to weak topics.
Include breaks and revision days.
The last 2 days should be reserved for full revision.

Return ONLY a valid JSON array of sessions:
[
  {{
    "date": "YYYY-MM-DD",
    "topics": ["Topic A", "Topic B"],
    "duration": 2.0,
    "resources": ["Document Name - Chapter/Section"]
  }}
]

JSON:"""


def create_study_plan(
    user_id: str,
    document_ids: List[str],
    exam_date: str,
    hours_per_day: float = 2.0,
    weak_topics: Optional[List[str]] = None,
) -> dict:
    """
    Generate a personalised study plan.

    Args:
        user_id:       The requesting user.
        document_ids:  Documents (subjects) to cover.
        exam_date:     Target exam date (YYYY-MM-DD).
        hours_per_day: How many hours the student can study daily.
        weak_topics:   Topics where the student scored low.

    Returns:
        {{plan_id, user_id, sessions, created_at}}
    """
    weak_topics = weak_topics or []
    db          = get_db()

    # Fetch document names for context
    subjects = []
    for doc_id in document_ids:
        doc = db.documents.find_one({"_id": doc_id})
        if doc:
            subjects.append(doc.get("original_name", doc_id))

    # Calculate days left
    try:
        exam_dt   = datetime.strptime(exam_date, "%Y-%m-%d").date()
        today     = date.today()
        days_left = (exam_dt - today).days
        if days_left <= 0:
            days_left = 1
    except ValueError:
        days_left = 14   # default 2 weeks

    prompt = _PLANNER_PROMPT.format(
        subjects      = ", ".join(subjects) or "General Study",
        days_left     = days_left,
        hours_per_day = hours_per_day,
        weak_topics   = ", ".join(weak_topics) if weak_topics else "None",
    )

    raw_out  = watsonx.generate(prompt, max_new_tokens=3000, temperature=0.4)
    sessions = _parse_sessions(raw_out, today, days_left, hours_per_day)

    plan_id = new_id()
    result  = {
        "plan_id":      plan_id,
        "user_id":      user_id,
        "document_ids": document_ids,
        "exam_date":    exam_date,
        "hours_per_day": hours_per_day,
        "sessions":     sessions,
        "created_at":   now_iso(),
    }

    db.study_plans.update_one(
        {"user_id": user_id},
        {"$set": result},
        upsert=True,
    )

    logger.info(f"[PlannerAgent] Plan created for user {user_id}: {len(sessions)} sessions")
    return result


def _parse_sessions(
    raw: str,
    today: date,
    days_left: int,
    hours_per_day: float,
) -> List[dict]:
    """Parse the model's JSON output; fall back to a basic plan if needed."""
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if match:
        try:
            sessions = json.loads(match.group())
            validated = []
            for s in sessions:
                if isinstance(s, dict) and "date" in s and "topics" in s:
                    validated.append({
                        "date":      s["date"],
                        "topics":    s.get("topics", []),
                        "duration":  s.get("duration", hours_per_day),
                        "resources": s.get("resources", []),
                    })
            if validated:
                return validated
        except json.JSONDecodeError:
            pass

    # Fallback: simple daily plan
    logger.warning("[PlannerAgent] JSON parse failed; generating fallback plan")
    sessions = []
    for i in range(days_left):
        day = today + timedelta(days=i)
        sessions.append({
            "date":      day.isoformat(),
            "topics":    ["Review all materials"] if i >= days_left - 2 else ["Study Session"],
            "duration":  hours_per_day,
            "resources": [],
        })
    return sessions
