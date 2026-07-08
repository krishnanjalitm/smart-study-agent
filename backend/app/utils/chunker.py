"""
smart-study-agent/backend/app/utils/chunker.py
Text chunking utilities for RAG ingestion.
Uses a sliding-window character-based splitter to produce overlapping chunks.
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(
    text: str,
    chunk_size: int    = 800,
    chunk_overlap: int = 150,
) -> List[str]:
    """
    Split *text* into overlapping chunks.

    Args:
        text:          Raw document text.
        chunk_size:    Target number of characters per chunk.
        chunk_overlap: Number of characters shared between consecutive chunks.

    Returns:
        List of text chunk strings.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_text(text)
    # Filter empty / whitespace-only chunks
    return [c.strip() for c in chunks if c.strip()]
