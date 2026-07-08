"""
smart-study-agent/backend/app/api/chat.py
AI Chat / RAG question-answering endpoint.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.rag_agent import answer_question
from app.agents.progress_agent import log_activity
from app.core.logger import logger

bp = Blueprint("chat", __name__)


@bp.route("/ask", methods=["POST"])
@jwt_required()
def ask():
    """
    POST /api/chat/ask
    Body: {
      "message": "Explain Newton's laws",
      "document_ids": ["abc", "def"],
      "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    }

    Returns: {"answer": "...", "sources": [...]}
    """
    user_id = get_jwt_identity()
    data    = request.get_json(silent=True) or {}

    message      = (data.get("message") or "").strip()
    document_ids = data.get("document_ids") or []
    history      = data.get("history") or []

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        result = answer_question(
            question     = message,
            document_ids = document_ids,
            history      = history,
        )
        log_activity(user_id, "chat_session", {"question_length": len(message)})
        return jsonify(result), 200
    except Exception as exc:
        logger.error(f"[ChatAPI] {exc}")
        return jsonify({"error": str(exc)}), 500
