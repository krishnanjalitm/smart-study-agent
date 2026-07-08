"""
smart-study-agent/backend/app/services/embedding_service.py
Generates text embeddings using IBM Slate (watsonx) or a local
sentence-transformer as a fallback for development environments.
"""

from typing import List
from app.core.config import settings
from app.core.logger import logger


class EmbeddingService:
    """
    Provides text→vector embeddings.
    Priority:
      1. IBM watsonx.ai Slate embeddings (production)
      2. sentence-transformers all-MiniLM-L6-v2 (local fallback)
    """

    def __init__(self):
        self._model = None
        self._mode  = "local"
        self._init_watsonx()
        if self._mode != "watsonx":
            self._init_local()

    # ── Initialisation ────────────────────────────────────────────────────────

    def _init_watsonx(self):
        """Try to use IBM watsonx embeddings."""
        if not settings.WATSONX_API_KEY:
            return
        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models.embeddings import Embeddings
            from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes

            creds = Credentials(
                url=settings.WATSONX_URL,
                api_key=settings.WATSONX_API_KEY,
            )
            self._watsonx_embedder = Embeddings(
                model_id=settings.GRANITE_EMBED_MODEL,
                credentials=creds,
                project_id=settings.WATSONX_PROJECT_ID,
            )
            self._mode = "watsonx"
            logger.info("Embedding mode: IBM watsonx Slate")
        except Exception as e:
            logger.warning(f"watsonx embeddings unavailable ({e}); falling back to local")

    def _init_local(self):
        """Fallback: sentence-transformers."""
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        self._mode  = "local"
        logger.info("Embedding mode: local sentence-transformers")

    # ── Public API ────────────────────────────────────────────────────────────

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Return embedding vectors for a list of text strings."""
        if self._mode == "watsonx":
            return self._embed_watsonx(texts)
        return self._embed_local(texts)

    def embed_query(self, text: str) -> List[float]:
        """Return a single embedding vector for a query string."""
        return self.embed([text])[0]

    # ── Backend implementations ───────────────────────────────────────────────

    def _embed_watsonx(self, texts: List[str]) -> List[List[float]]:
        results = self._watsonx_embedder.embed_documents(texts)
        return [r["embedding"] for r in results]

    def _embed_local(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()


# Module-level singleton
embedding_service = EmbeddingService()
