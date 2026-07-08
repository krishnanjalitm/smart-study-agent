"""
smart-study-agent/backend/app/agents/document_agent.py
Document Processing Agent
─────────────────────────
Responsibility:
  1. Save the uploaded file to disk.
  2. Extract text (PDF / DOCX / TXT / Image).
  3. Chunk the text for RAG.
  4. Generate & store embeddings in ChromaDB.
  5. Persist document metadata to MongoDB.
"""

import os
import uuid
from datetime import datetime
from werkzeug.datastructures import FileStorage

from app.core.config import settings
from app.core.logger import logger
from app.db.mongo import get_db
from app.db.chroma import get_or_create_collection
from app.utils.file_parser import extract_text
from app.utils.chunker import chunk_text
from app.utils.helpers import now_iso
from app.services.embedding_service import embedding_service


def process_document(file: FileStorage, user_id: str) -> dict:
    """
    Full pipeline: save → extract → chunk → embed → store.

    Returns the MongoDB document dict with an 'id' field.
    """
    # ── 1. Save file ──────────────────────────────────────────────────────────
    doc_id    = str(uuid.uuid4())
    ext       = file.filename.rsplit(".", 1)[-1].lower()
    safe_name = f"{doc_id}.{ext}"
    save_path = os.path.join(settings.UPLOAD_FOLDER, safe_name)

    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    file.save(save_path)
    file_size = os.path.getsize(save_path)
    logger.info(f"[DocAgent] Saved {file.filename} → {save_path}")

    # ── 2. Extract text ───────────────────────────────────────────────────────
    try:
        raw_text, page_count, word_count = extract_text(save_path)
        status = "ready"
    except Exception as exc:
        logger.error(f"[DocAgent] Text extraction failed: {exc}")
        raw_text, page_count, word_count = "", 0, 0
        status = "error"

    # ── 3. Chunk ──────────────────────────────────────────────────────────────
    chunks = chunk_text(raw_text) if raw_text else []

    # ── 4. Embed & store in ChromaDB ──────────────────────────────────────────
    if chunks:
        try:
            collection_name = f"doc_{doc_id.replace('-', '_')}"
            collection      = get_or_create_collection(collection_name)
            embeddings      = embedding_service.embed(chunks)

            collection.upsert(
                ids        = [f"{doc_id}_{i}" for i in range(len(chunks))],
                documents  = chunks,
                embeddings = embeddings,
                metadatas  = [
                    {
                        "document_id":  doc_id,
                        "chunk_index":  i,
                        "user_id":      user_id,
                        "source_file":  file.filename,
                    }
                    for i in range(len(chunks))
                ],
            )
            logger.info(f"[DocAgent] Indexed {len(chunks)} chunks for doc {doc_id}")
        except Exception as exc:
            logger.error(f"[DocAgent] ChromaDB indexing failed: {exc}")

    # ── 5. Persist metadata to MongoDB ────────────────────────────────────────
    doc_record = {
        "_id":          doc_id,
        "user_id":      user_id,
        "filename":     safe_name,
        "original_name": file.filename,
        "file_type":    ext,
        "file_size":    file_size,
        "status":       status,
        "page_count":   page_count,
        "word_count":   word_count,
        "chunk_count":  len(chunks),
        "raw_text":     raw_text[:5000],   # store preview only
        "created_at":   now_iso(),
        "tags":         [],
    }

    db = get_db()
    db.documents.insert_one(doc_record)
    logger.info(f"[DocAgent] Document {doc_id} persisted to MongoDB")

    # Return serialisable version
    doc_record["id"] = doc_record.pop("_id")
    return doc_record
