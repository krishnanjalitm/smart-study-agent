"""
smart-study-agent/backend/app/api/flashcards.py
Flashcard generation and retrieval endpoints.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.flashcard_agent import generate_flashcards
from app.agents.progress_agent import log_activity
from app.db.mongo import get_db
from app.core.logger import logger

bp = Blueprint("flashcards", __name__)


@bp.route("/generate", methods=["POST"])
@jwt_required()
def create_flashcards():
    """
    POST /api/flashcards/generate
    Body: {"document_id": "...", "count": 10}
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    doc_id  = data.get("document_id")
    count   = int(data.get("count", 10))

    if not doc_id:
        return jsonify({"error": "document_id is required"}), 400
    if not (1 <= count <= 50):
        return jsonify({"error": "count must be between 1 and 50"}), 400

    db  = get_db()
    doc = db.documents.find_one({"_id": doc_id, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    try:
        result = generate_flashcards(doc_id, count)
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"[FlashcardAPI] {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/<doc_id>", methods=["GET"])
@jwt_required()
def get_flashcards(doc_id: str):
    """GET /api/flashcards/<doc_id> — return cached flashcard set."""
    user_id = get_jwt_identity()
    db      = get_db()

    doc = db.documents.find_one({"_id": doc_id, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    cached = db.flashcards.find_one({"document_id": doc_id})
    if not cached:
        return jsonify({"error": "No flashcards found. Please generate them first."}), 404

    cached.pop("_id", None)
    return jsonify(cached), 200


@bp.route("/reviewed", methods=["POST"])
@jwt_required()
def mark_reviewed():
    """
    POST /api/flashcards/reviewed
    Body: {"document_id": "...", "count": 5}
    Log that the student reviewed N flashcards.
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    count   = int(data.get("count", 1))
    log_activity(user_id, "flashcard_reviewed", {"count": count})
    return jsonify({"status": "logged"}), 200
