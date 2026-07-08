"""
smart-study-agent/backend/app/db/mongo.py
MongoDB connection and collection accessors.
Uses PyMongo (sync) behind Flask request context.
"""

from flask import Flask
from pymongo import MongoClient
from pymongo.database import Database
from app.core.config import settings
from app.core.logger import logger

_client: MongoClient = None
_db: Database = None


def init_mongo(app: Flask) -> None:
    """Initialise MongoClient and attach teardown hook."""
    global _client, _db
    _client = MongoClient(settings.MONGO_URI)
    _db = _client[settings.MONGO_DB_NAME]
    logger.info(f"MongoDB connected → {settings.MONGO_DB_NAME}")

    # Create indexes on startup
    _db.users.create_index("email", unique=True)
    _db.documents.create_index("user_id")
    _db.flashcards.create_index("document_id")
    _db.quizzes.create_index("document_id")
    _db.study_plans.create_index("user_id")
    _db.progress.create_index([("user_id", 1), ("date", -1)])

    @app.teardown_appcontext
    def close_mongo(exc):
        pass  # MongoClient is process-level; keep it alive


def get_db() -> Database:
    """Return the active database instance."""
    if _db is None:
        raise RuntimeError("MongoDB not initialised. Call init_mongo() first.")
    return _db
