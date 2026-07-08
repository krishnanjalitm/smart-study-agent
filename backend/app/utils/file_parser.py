"""
smart-study-agent/backend/app/utils/file_parser.py
Extracts plain text from PDF, DOCX, TXT, and image files (OCR via Tesseract).
"""

import io
import os
from pathlib import Path
from typing import Tuple

import PyPDF2
from docx import Document as DocxDocument
from PIL import Image
import pytesseract

from app.core.logger import logger


def extract_text(file_path: str) -> Tuple[str, int, int]:
    """
    Extract text from the given file path.

    Returns:
        (text, page_count, word_count)
    """
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext == ".docx":
        return _extract_docx(file_path)
    elif ext == ".txt":
        return _extract_txt(file_path)
    elif ext in {".png", ".jpg", ".jpeg"}:
        return _extract_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _extract_pdf(path: str) -> Tuple[str, int, int]:
    """Extract text from PDF using PyPDF2."""
    pages = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)
    full_text  = "\n".join(pages)
    word_count = len(full_text.split())
    logger.debug(f"PDF extracted: {len(pages)} pages, {word_count} words")
    return full_text, len(pages), word_count


def _extract_docx(path: str) -> Tuple[str, int, int]:
    """Extract text from DOCX."""
    doc   = DocxDocument(path)
    lines = [para.text for para in doc.paragraphs if para.text.strip()]
    full_text  = "\n".join(lines)
    word_count = len(full_text.split())
    logger.debug(f"DOCX extracted: {word_count} words")
    return full_text, 1, word_count


def _extract_txt(path: str) -> Tuple[str, int, int]:
    """Read plain text file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        full_text = f.read()
    word_count = len(full_text.split())
    return full_text, 1, word_count


def _extract_image(path: str) -> Tuple[str, int, int]:
    """OCR an image using Tesseract."""
    img       = Image.open(path)
    full_text = pytesseract.image_to_string(img)
    word_count = len(full_text.split())
    logger.debug(f"Image OCR: {word_count} words extracted")
    return full_text, 1, word_count
