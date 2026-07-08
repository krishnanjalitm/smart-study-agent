"""
smart-study-agent/backend/app/utils/helpers.py
Miscellaneous utility functions.
"""

import uuid
from datetime import datetime
from bson import ObjectId


def new_id() -> str:
    """Generate a URL-safe UUID4 string."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.utcnow().isoformat() + "Z"


def bson_to_dict(doc: dict) -> dict:
    """
    Recursively convert MongoDB BSON ObjectIds to plain strings
    so the document can be JSON-serialised.
    """
    if doc is None:
        return {}
    result = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            result[k] = str(v)
        elif isinstance(v, dict):
            result[k] = bson_to_dict(v)
        elif isinstance(v, list):
            result[k] = [bson_to_dict(i) if isinstance(i, dict) else i for i in v]
        else:
            result[k] = v
    return result


def paginate(query_result, page: int, per_page: int) -> dict:
    """
    Paginate a list of items.

    Returns a dict with: items, page, per_page, total.
    """
    total  = len(query_result)
    start  = (page - 1) * per_page
    end    = start + per_page
    return {
        "items":    query_result[start:end],
        "page":     page,
        "per_page": per_page,
        "total":    total,
    }
