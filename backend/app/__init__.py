"""
smart-study-agent/backend/app/__init__.py
Application factory — wires together Flask, JWT, CORS, MongoDB, ChromaDB,
and all API blueprints.
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from app.core.config import settings
from app.core.logger import logger
from app.db.mongo import init_mongo
from app.db.chroma import init_chroma
from app.api import auth, documents, summary, flashcards, quiz, planner, progress, chat


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # ── Core config ────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = settings.MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = settings.UPLOAD_FOLDER

    # ── Extensions ─────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    # ── Database initialisation ────────────────────────────────────────────────
    init_mongo(app)
    init_chroma()

    # ── Register blueprints ────────────────────────────────────────────────────
    app.register_blueprint(auth.bp,       url_prefix="/api/auth")
    app.register_blueprint(documents.bp,  url_prefix="/api/documents")
    app.register_blueprint(summary.bp,    url_prefix="/api/summary")
    app.register_blueprint(flashcards.bp, url_prefix="/api/flashcards")
    app.register_blueprint(quiz.bp,       url_prefix="/api/quiz")
    app.register_blueprint(planner.bp,    url_prefix="/api/planner")
    app.register_blueprint(progress.bp,   url_prefix="/api/progress")
    app.register_blueprint(chat.bp,       url_prefix="/api/chat")

    logger.info("Smart Study Agent application started")
    return app
