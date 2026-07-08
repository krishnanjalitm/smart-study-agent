"""
smart-study-agent/backend/app/agents/rag_agent.py
Question Answering (RAG) Agent
────────────────────────────────
Responsibility:
  1. Embed the user's question.
  2. Retrieve top-k semantically similar chunks from ChromaDB.
  3. Build a context-aware prompt with source attribution.
  4. Call IBM Granite via WatsonxClient.
  5. Return the answer plus cited source chunks.
"""

from typing import List, Optional
from app.core.logger import logger
from app.db.chroma import get_or_create_collection
from app.db.mongo import get_db
from app.services.embedding_service import embedding_service
from app.services.watsonx_client import watsonx


# ── Prompt template ───────────────────────────────────────────────────────────

_RAG_PROMPT = """You are an expert academic tutor. Use ONLY the context passages provided below to answer the student's question. If the answer cannot be found in the context, say "I don't have enough information in the uploaded materials to answer this question."

<context>
{context}
</context>

<conversation_history>
{history}
</conversation_history>

Student question: {question}

Provide a clear, well-structured answer with examples where helpful. Always cite the source passages you used.

Answer:"""


def answer_question(
    question: str,
    document_ids: List[str],
    history: Optional[List[dict]] = None,
    top_k: int = 5,
) -> dict:
    """
    RAG pipeline entry point.

    Args:
        question:     The student's question.
        document_ids: List of document IDs to search.
        history:      Prior conversation turns [{role, content}].
        top_k:        Number of chunks to retrieve per document.

    Returns:
        {"answer": str, "sources": [SourceChunk dicts]}
    """
    history = history or []

    # ── 1. Embed query ────────────────────────────────────────────────────────
    query_embedding = embedding_service.embed_query(question)

    # ── 2. Retrieve chunks from each requested document ───────────────────────
    all_chunks: List[dict] = []

    if document_ids:
        for doc_id in document_ids:
            coll_name = f"doc_{doc_id.replace('-', '_')}"
            try:
                collection = get_or_create_collection(coll_name)
                results    = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    include=["documents", "metadatas", "distances"],
                )
                for text, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                ):
                    all_chunks.append({
                        "chunk_text":    text,
                        "document_id":   doc_id,
                        "chunk_index":   meta.get("chunk_index", 0),
                        "source_file":   meta.get("source_file", ""),
                        "score":         round(1 - dist, 4),   # cosine similarity
                    })
            except Exception as exc:
                logger.warning(f"[RAGAgent] Failed querying doc {doc_id}: {exc}")

        # Sort by relevance score (descending)
        all_chunks.sort(key=lambda x: x["score"], reverse=True)
        all_chunks = all_chunks[:top_k]

    # ── 3. Enrich with document names from MongoDB ────────────────────────────
    db     = get_db()
    sources = []
    for chunk in all_chunks:
        doc = db.documents.find_one({"_id": chunk["document_id"]})
        chunk["document_name"] = doc.get("original_name", "Unknown") if doc else "Unknown"
        sources.append(chunk)

    # ── 4. Build context string ───────────────────────────────────────────────
    context_lines = []
    for i, s in enumerate(sources, 1):
        context_lines.append(
            f"[Source {i}: {s['document_name']}]\n{s['chunk_text']}"
        )
    context = "\n\n".join(context_lines) if context_lines else "No documents provided."

    # ── 5. Build history string ───────────────────────────────────────────────
    history_text = ""
    for turn in history[-6:]:   # last 3 user-assistant pairs
        role    = turn.get("role", "user").capitalize()
        content = turn.get("content", "")
        history_text += f"{role}: {content}\n"

    # ── 6. Generate answer ────────────────────────────────────────────────────
    prompt = _RAG_PROMPT.format(
        context=context,
        history=history_text.strip(),
        question=question,
    )
    answer = watsonx.generate(prompt, max_new_tokens=1024, temperature=0.3)
    logger.info(f"[RAGAgent] Generated answer ({len(answer)} chars) for question: {question[:60]}")

    return {"answer": answer, "sources": sources}
