"""
smart-study-agent/tests/backend/test_api.py
Integration tests for the Flask API endpoints.
Run: pytest tests/backend/ -v
"""

import pytest
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend"))

from unittest.mock import patch, MagicMock


@pytest.fixture
def client():
    """Create a Flask test client with mocked DB."""
    with patch("app.db.mongo.init_mongo"), \
         patch("app.db.chroma.init_chroma"), \
         patch("app.services.embedding_service.EmbeddingService.__init__", return_value=None):
        from app import create_app
        app = create_app()
        app.config["TESTING"] = True
        app.config["JWT_SECRET_KEY"] = "test-secret"
        with app.test_client() as client:
            yield client


# ── Auth Tests ────────────────────────────────────────────────────────────────

class TestAuth:
    def test_register_missing_fields(self, client):
        """Registration without required fields returns 400."""
        resp = client.post("/api/auth/register",
                           json={"email": "test@test.com"},
                           content_type="application/json")
        assert resp.status_code == 400

    def test_register_success(self, client):
        """Successful registration returns 201 with tokens."""
        mock_db = MagicMock()
        mock_db.users.find_one.return_value = None
        mock_db.users.insert_one.return_value = MagicMock(inserted_id="abc123")

        with patch("app.api.auth.get_db", return_value=mock_db):
            resp = client.post("/api/auth/register", json={
                "name":     "Test User",
                "email":    "test@example.com",
                "password": "password123",
            })
        assert resp.status_code == 201
        data = resp.get_json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_register_duplicate_email(self, client):
        """Duplicate email returns 409."""
        mock_db = MagicMock()
        mock_db.users.find_one.return_value = {"email": "test@example.com"}

        with patch("app.api.auth.get_db", return_value=mock_db):
            resp = client.post("/api/auth/register", json={
                "name": "Test", "email": "test@example.com", "password": "pass1234",
            })
        assert resp.status_code == 409

    def test_login_wrong_password(self, client):
        """Wrong password returns 401."""
        from app.core.security import hash_password
        mock_db = MagicMock()
        mock_db.users.find_one.return_value = {
            "_id": "abc", "password": hash_password("correct_password")
        }
        with patch("app.api.auth.get_db", return_value=mock_db):
            resp = client.post("/api/auth/login", json={
                "email": "test@example.com", "password": "wrong_password"
            })
        assert resp.status_code == 401


# ── Document Tests ─────────────────────────────────────────────────────────────

class TestDocuments:
    def _get_token(self, client):
        """Helper to get a valid JWT access token."""
        mock_db = MagicMock()
        mock_db.users.find_one.return_value = None
        mock_db.users.insert_one.return_value = MagicMock(inserted_id="user123")
        with patch("app.api.auth.get_db", return_value=mock_db):
            resp = client.post("/api/auth/register", json={
                "name": "T", "email": "t@t.com", "password": "testpass1"
            })
        return resp.get_json().get("access_token", "")

    def test_upload_no_file(self, client):
        """Upload without file returns 400."""
        token = self._get_token(client)
        resp  = client.post("/api/documents/upload",
                            headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400

    def test_list_documents_requires_auth(self, client):
        """Document list without JWT returns 401."""
        resp = client.get("/api/documents/")
        assert resp.status_code == 401


# ── RAG / Chat Tests ───────────────────────────────────────────────────────────

class TestChat:
    def test_chat_empty_message(self, client):
        """Empty message returns 400."""
        mock_db = MagicMock()
        mock_db.users.find_one.return_value = None
        mock_db.users.insert_one.return_value = MagicMock(inserted_id="u1")
        with patch("app.api.auth.get_db", return_value=mock_db):
            resp = client.post("/api/auth/register", json={
                "name": "X", "email": "x@x.com", "password": "xpassword"
            })
        token = resp.get_json().get("access_token", "")

        resp2 = client.post("/api/chat/ask",
                            json={"message": ""},
                            headers={"Authorization": f"Bearer {token}"})
        assert resp2.status_code == 400


# ── Utility Tests ─────────────────────────────────────────────────────────────

class TestSecurity:
    def test_password_hash_and_verify(self):
        from app.core.security import hash_password, verify_password
        plain  = "supersecret123"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)
        assert not verify_password("wrongpass", hashed)

    def test_generate_tokens(self):
        """Tokens are non-empty strings."""
        with patch("app.core.security.create_access_token",  return_value="access_tok"), \
             patch("app.core.security.create_refresh_token", return_value="refresh_tok"):
            from app.core.security import generate_tokens
            tokens = generate_tokens("user_id_123")
        assert tokens["access_token"]  == "access_tok"
        assert tokens["refresh_token"] == "refresh_tok"


class TestChunker:
    def test_chunk_text_basic(self):
        from app.utils.chunker import chunk_text
        long_text = "word " * 1000
        chunks    = chunk_text(long_text, chunk_size=200, chunk_overlap=20)
        assert len(chunks) > 1
        for c in chunks:
            assert len(c) <= 250   # chunks may be slightly larger due to word boundaries

    def test_chunk_empty_text(self):
        from app.utils.chunker import chunk_text
        chunks = chunk_text("", chunk_size=200)
        assert chunks == []
