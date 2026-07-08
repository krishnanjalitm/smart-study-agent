"""
smart-study-agent/backend/app/db/chroma.py
ChromaDB persistent vector store — one collection per user document.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from app.core.logger import logger

_client: chromadb.ClientAPI = None


def init_chroma() -> None:
    """Create or connect to the persistent ChromaDB instance."""
    global _client
    _client = chromadb.PersistentClient(
        path=settings.CHROMA_PERSIST_DIR,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    logger.info(f"ChromaDB ready → {settings.CHROMA_PERSIST_DIR}")


def get_or_create_collection(collection_name: str) -> chromadb.Collection:
    """
    Return an existing ChromaDB collection or create it.
    Collection names are scoped per document: 'doc_<document_id>'.
    """
    if _client is None:
        raise RuntimeError("ChromaDB not initialised. Call init_chroma() first.")
    return _client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def delete_collection(collection_name: str) -> None:
    """Delete a ChromaDB collection (called when a document is deleted)."""
    if _client:
        try:
            _client.delete_collection(collection_name)
        except Exception:
            pass
