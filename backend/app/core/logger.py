"""
smart-study-agent/backend/app/core/logger.py
Structured application logger using loguru.
"""

import sys
from pathlib import Path
from loguru import logger

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Remove default handler
logger.remove()

# Console — coloured, human-readable
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# Rotating file — JSON-friendly, kept 7 days
logger.add(
    LOG_DIR / "app.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
    level="INFO",
    enqueue=True,
)

__all__ = ["logger"]
