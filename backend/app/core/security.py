"""
smart-study-agent/backend/app/core/security.py
Password hashing helpers and JWT utilities.
"""

import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta


def hash_password(plain: str) -> str:
    """Return a bcrypt-hashed password string."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches hashed."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def generate_tokens(user_id: str) -> dict:
    """
    Generate an access token (15 min) and a refresh token (30 days)
    for the given user_id string.
    """
    access  = create_access_token(identity=user_id, expires_delta=timedelta(minutes=15))
    refresh = create_refresh_token(identity=user_id, expires_delta=timedelta(days=30))
    return {"access_token": access, "refresh_token": refresh}
