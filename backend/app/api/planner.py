"""
smart-study-agent/backend/app/api/planner.py
Study plan generation and retrieval.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.planner_agent import create_study_plan
from app.db.mongo import get_db
from app.core.logger import logger

bp = Blueprint("planner", __name__)


@bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_plan():
    """
    POST /api/planner/generate
    Body: {
      "document_ids": ["..."],
      "exam_date": "2025-06-01",
      "hours_per_day": 3.0,
      "weak_topics": ["Integration", "Thermodynamics"]
    }
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}

    doc_ids       = data.get("document_ids", [])
    exam_date     = data.get("exam_date")
    hours_per_day = float(data.get("hours_per_day", 2.0))
    weak_topics   = data.get("weak_topics", [])

    if not exam_date:
        return jsonify({"error": "exam_date is required (YYYY-MM-DD)"}), 400

    try:
        result = create_study_plan(
            user_id       = user_id,
            document_ids  = doc_ids,
            exam_date     = exam_date,
            hours_per_day = hours_per_day,
            weak_topics   = weak_topics,
        )
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"[PlannerAPI] {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/", methods=["GET"])
@jwt_required()
def get_plan():
    """GET /api/planner/ — return the current user's study plan."""
    user_id = get_jwt_identity()
    db      = get_db()
    plan    = db.study_plans.find_one({"user_id": user_id}, {"_id": 0})
    if not plan:
        return jsonify({"error": "No study plan found. Generate one first."}), 404
    return jsonify(plan), 200
