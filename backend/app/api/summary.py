"""
smart-study-agent/backend/app/api/summary.py
Summary generation and retrieval endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.summary_agent import generate_summary
from app.db.mongo import get_db
from app.core.logger import logger
from app.agents.progress_agent import log_activity

bp = Blueprint("summary", __name__)


@bp.route("/generate", methods=["POST"])
@jwt_required()
def create_summary():
    """
    POST /api/summary/generate
    Body: {"document_id": "...", "length": "short|medium|detailed"}
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    doc_id  = data.get("document_id")
    length  = data.get("length", "medium")

    if not doc_id:
        return jsonify({"error": "document_id is required"}), 400
    if length not in ("short", "medium", "detailed"):
        return jsonify({"error": "length must be short, medium, or detailed"}), 400

    # Verify ownership
    db  = get_db()
    doc = db.documents.find_one({"_id": doc_id, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    try:
        result = generate_summary(doc_id, length)
        log_activity(user_id, "document_read", {"document_id": doc_id})
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"[SummaryAPI] {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/<doc_id>", methods=["GET"])
@jwt_required()
def get_summary(doc_id: str):
    """
    GET /api/summary/<doc_id>?length=medium
    Return a cached summary if available, otherwise generate it.
    """
    user_id = get_jwt_identity()
    length  = request.args.get("length", "medium")

    db = get_db()
    # Check cache
    cached = db.summaries.find_one({"document_id": doc_id, "length": length})
    if cached:
        cached.pop("_id", None)
        return jsonify(cached), 200

    # Verify ownership and generate
    doc = db.documents.find_one({"_id": doc_id, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    try:
        result = generate_summary(doc_id, length)
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"[SummaryAPI] {exc}")
        return jsonify({"error": str(exc)}), 500
