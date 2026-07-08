"""
smart-study-agent/backend/app/api/progress.py
Study progress dashboard and activity logging.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.progress_agent import get_dashboard, log_activity
from app.core.logger import logger

bp = Blueprint("progress", __name__)


@bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    """GET /api/progress/dashboard — return aggregated learning analytics."""
    user_id = get_jwt_identity()
    try:
        data = get_dashboard(user_id)
        return jsonify(data), 200
    except Exception as exc:
        logger.error(f"[ProgressAPI] {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/log", methods=["POST"])
@jwt_required()
def log_event():
    """
    POST /api/progress/log
    Body: {"activity_type": "document_read", "details": {"document_id": "..."}}
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    atype   = data.get("activity_type")
    details = data.get("details", {})

    if not atype:
        return jsonify({"error": "activity_type is required"}), 400

    result = log_activity(user_id, atype, details)
    return jsonify(result), 200
