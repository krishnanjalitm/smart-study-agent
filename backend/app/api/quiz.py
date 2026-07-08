"""
smart-study-agent/backend/app/api/quiz.py
Quiz generation, submission, and result retrieval.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.quiz_agent import generate_quiz, evaluate_quiz
from app.agents.progress_agent import log_activity
from app.db.mongo import get_db
from app.utils.helpers import bson_to_dict
from app.core.logger import logger

bp = Blueprint("quiz", __name__)


@bp.route("/generate", methods=["POST"])
@jwt_required()
def create_quiz():
    """
    POST /api/quiz/generate
    Body: {
      "document_id": "...",
      "question_types": ["mcq", "true_false"],
      "count": 10
    }
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    doc_id  = data.get("document_id")
    qtypes  = data.get("question_types", ["mcq"])
    count   = int(data.get("count", 10))

    if not doc_id:
        return jsonify({"error": "document_id is required"}), 400

    db  = get_db()
    doc = db.documents.find_one({"_id": doc_id, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    valid_types = {"mcq", "true_false", "short_answer"}
    qtypes = [t for t in qtypes if t in valid_types] or ["mcq"]

    try:
        result = generate_quiz(doc_id, qtypes, count)
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"[QuizAPI] {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_quiz():
    """
    POST /api/quiz/submit
    Body: {"quiz_id": "...", "answers": {"q_id": "A", ...}}
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}
    quiz_id = data.get("quiz_id")
    answers = data.get("answers", {})

    if not quiz_id:
        return jsonify({"error": "quiz_id is required"}), 400

    try:
        result = evaluate_quiz(quiz_id, answers)
        # Log quiz completion for progress tracking
        log_activity(user_id, "quiz_completed", {
            "quiz_id": quiz_id,
            "score":   result["score"],
            "minutes": 15,   # estimate
        })
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.error(f"[QuizAPI] Submit failed: {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/history", methods=["GET"])
@jwt_required()
def quiz_history():
    """GET /api/quiz/history — list all quizzes for the current user's documents."""
    user_id = get_jwt_identity()
    db      = get_db()

    # Get doc IDs owned by user
    doc_ids = [d["_id"] for d in db.documents.find({"user_id": user_id}, {"_id": 1})]
    quizzes = list(db.quizzes.find(
        {"document_id": {"$in": doc_ids}},
        {"questions": 0},   # exclude question bodies for the list view
    ))
    result = [bson_to_dict(q) for q in quizzes]
    return jsonify({"quizzes": result}), 200
