"""
smart-study-agent/backend/app/api/documents.py
Document management: upload, list, get, delete, search.
"""

from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.agents.document_agent import process_document
from app.db.mongo import get_db
from app.db.chroma import delete_collection
from app.core.config import settings
from app.core.logger import logger
from app.utils.helpers import bson_to_dict, paginate

bp = Blueprint("documents", __name__)


@bp.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    """
    POST /api/documents/upload
    Multipart form: file (required), tags (optional, comma-separated string)
    """
    user_id = get_jwt_identity()

    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not settings.allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"}), 415

    try:
        doc = process_document(file, user_id)

        # Apply optional tags
        raw_tags = request.form.get("tags", "")
        if raw_tags:
            tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            db = get_db()
            db.documents.update_one({"_id": doc["id"]}, {"$set": {"tags": tags}})
            doc["tags"] = tags

        return jsonify(doc), 201
    except Exception as exc:
        logger.error(f"[DocAPI] Upload failed: {exc}")
        return jsonify({"error": str(exc)}), 500


@bp.route("/", methods=["GET"])
@jwt_required()
def list_documents():
    """
    GET /api/documents/?page=1&per_page=20&tag=math
    List all documents for the authenticated user.
    """
    user_id  = get_jwt_identity()
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    tag      = request.args.get("tag")

    db    = get_db()
    query = {"user_id": user_id}
    if tag:
        query["tags"] = tag

    docs = [bson_to_dict(d) for d in db.documents.find(query, {"raw_text": 0}).sort("created_at", -1)]
    # Normalise _id → id
    for d in docs:
        if "_id" in d:
            d["id"] = d.pop("_id")

    return jsonify(paginate(docs, page, per_page)), 200


@bp.route("/<doc_id>", methods=["GET"])
@jwt_required()
def get_document(doc_id: str):
    """GET /api/documents/<doc_id> — fetch document metadata."""
    user_id = get_jwt_identity()
    db      = get_db()
    doc     = db.documents.find_one({"_id": doc_id, "user_id": user_id}, {"raw_text": 0})
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    result = bson_to_dict(doc)
    result["id"] = result.pop("_id", doc_id)
    return jsonify(result), 200


@bp.route("/<doc_id>", methods=["DELETE"])
@jwt_required()
def delete_document(doc_id: str):
    """DELETE /api/documents/<doc_id> — remove document and its vectors."""
    user_id = get_jwt_identity()
    db      = get_db()
    doc     = db.documents.find_one({"_id": doc_id, "user_id": user_id})
    if not doc:
        return jsonify({"error": "Document not found"}), 404

    # Remove from MongoDB
    db.documents.delete_one({"_id": doc_id})
    db.summaries.delete_many({"document_id": doc_id})
    db.flashcards.delete_many({"document_id": doc_id})
    db.quizzes.delete_many({"document_id": doc_id})

    # Remove from ChromaDB
    delete_collection(f"doc_{doc_id.replace('-', '_')}")

    logger.info(f"[DocAPI] Document {doc_id} deleted by user {user_id}")
    return jsonify({"message": "Document deleted"}), 200


@bp.route("/search", methods=["GET"])
@jwt_required()
def search():
    """
    GET /api/documents/search?q=<query>
    Full-text search across document metadata and stored text previews.
    """
    user_id = get_jwt_identity()
    q       = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []}), 200

    db   = get_db()
    docs = list(db.documents.find(
        {
            "user_id": user_id,
            "$or": [
                {"original_name": {"$regex": q, "$options": "i"}},
                {"raw_text":      {"$regex": q, "$options": "i"}},
                {"tags":          {"$regex": q, "$options": "i"}},
            ],
        },
        {"raw_text": 0},
    ))

    results = []
    for d in docs:
        item = bson_to_dict(d)
        item["id"] = item.pop("_id", "")
        results.append(item)

    return jsonify({"results": results, "total": len(results)}), 200
