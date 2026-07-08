"""
smart-study-agent/backend/app/api/auth.py
Authentication endpoints: register, login, refresh, profile.
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from app.core.security import hash_password, verify_password, generate_tokens
from app.core.logger import logger
from app.db.mongo import get_db
from app.models.schemas import RegisterRequest, LoginRequest
from app.utils.helpers import now_iso

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register — create a new user account."""
    data = request.get_json(silent=True) or {}
    try:
        payload = RegisterRequest(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    db = get_db()

    # Check duplicate email
    if db.users.find_one({"email": payload.email}):
        return jsonify({"error": "Email already registered"}), 409

    user = {
        "name":        payload.name,
        "email":       payload.email,
        "password":    hash_password(payload.password),
        "created_at":  now_iso(),
        "role":        "student",
        "avatar":      None,
    }
    result = db.users.insert_one(user)
    user_id = str(result.inserted_id)

    tokens  = generate_tokens(user_id)
    logger.info(f"[Auth] New user registered: {payload.email}")
    return jsonify({
        **tokens,
        "user": {"id": user_id, "name": payload.name, "email": payload.email},
    }), 201


@bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login — validate credentials and return JWT."""
    data = request.get_json(silent=True) or {}
    try:
        payload = LoginRequest(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    db   = get_db()
    user = db.users.find_one({"email": payload.email})

    if not user or not verify_password(payload.password, user["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    user_id = str(user["_id"])
    tokens  = generate_tokens(user_id)
    logger.info(f"[Auth] Login: {payload.email}")
    return jsonify({
        **tokens,
        "user": {
            "id":    user_id,
            "name":  user["name"],
            "email": user["email"],
        },
    }), 200


@bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """POST /api/auth/refresh — issue a new access token."""
    user_id    = get_jwt_identity()
    new_access = create_access_token(identity=user_id)
    return jsonify({"access_token": new_access}), 200


@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """GET /api/auth/me — return the current user's profile."""
    user_id = get_jwt_identity()
    db      = get_db()
    from bson import ObjectId
    user    = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id":         str(user["_id"]),
        "name":       user["name"],
        "email":      user["email"],
        "created_at": user.get("created_at"),
        "role":       user.get("role", "student"),
    }), 200
