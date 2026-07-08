"""
smart-study-agent/backend/app/core/config.py
Centralised settings loaded from environment variables (.env file).
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend root
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class Settings:
    # ── Flask ──────────────────────────────────────────────────────────────────
    FLASK_ENV: str              = os.getenv("FLASK_ENV", "development")
    SECRET_KEY: str             = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY: str         = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    MAX_CONTENT_LENGTH: int     = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))

    # ── MongoDB ────────────────────────────────────────────────────────────────
    MONGO_URI: str              = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str          = os.getenv("MONGO_DB_NAME", "smart_study_db")

    # ── ChromaDB ──────────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str     = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")

    # ── IBM watsonx.ai ────────────────────────────────────────────────────────
    WATSONX_API_KEY: str        = os.getenv("WATSONX_API_KEY", "")
    WATSONX_PROJECT_ID: str     = os.getenv("WATSONX_PROJECT_ID", "")
    WATSONX_URL: str            = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

    # ── Granite Models ────────────────────────────────────────────────────────
    GRANITE_MODEL_ID: str       = os.getenv("GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")
    GRANITE_EMBED_MODEL: str    = os.getenv("GRANITE_EMBED_MODEL", "ibm/slate-125m-english-rtrvr")

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: str              = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ── File Upload ───────────────────────────────────────────────────────────
    UPLOAD_FOLDER: str          = os.getenv("UPLOAD_FOLDER", "./uploads")
    ALLOWED_EXTENSIONS: set     = {"pdf", "docx", "txt", "png", "jpg", "jpeg"}

    # ── Langflow ──────────────────────────────────────────────────────────────
    LANGFLOW_API_URL: str       = os.getenv("LANGFLOW_API_URL", "http://localhost:7860")
    LANGFLOW_API_KEY: str       = os.getenv("LANGFLOW_API_KEY", "")

    def allowed_file(self, filename: str) -> bool:
        """Return True if the filename has an allowed extension."""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED_EXTENSIONS
        )


settings = Settings()
