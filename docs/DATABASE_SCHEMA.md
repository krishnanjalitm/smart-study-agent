# Database Schema — Smart Study Generator Agent

## MongoDB Collections

### `users`
```json
{
  "_id":        "ObjectId",
  "name":       "Jane Smith",
  "email":      "jane@example.com",
  "password":   "$2b$12$...",
  "role":       "student",
  "avatar":     null,
  "created_at": "2024-02-01T10:00:00Z"
}
```
**Indexes:** `email` (unique)

---

### `documents`
```json
{
  "_id":           "uuid-string",
  "user_id":       "ObjectId (string)",
  "filename":      "uuid.pdf",
  "original_name": "Biology Notes.pdf",
  "file_type":     "pdf",
  "file_size":     204800,
  "status":        "ready",
  "page_count":    12,
  "word_count":    3450,
  "chunk_count":   28,
  "raw_text":      "first 5000 chars...",
  "tags":          ["biology", "cells"],
  "created_at":    "2024-02-01T10:00:00Z"
}
```
**Indexes:** `user_id`

---

### `summaries`
```json
{
  "_id":         "ObjectId",
  "document_id": "uuid",
  "length":      "medium",
  "content":     "This document covers...",
  "created_at":  "2024-02-01T10:05:00Z"
}
```
**Unique constraint:** `(document_id, length)`

---

### `flashcards`
```json
{
  "_id":         "ObjectId",
  "document_id": "uuid",
  "set_id":      "uuid",
  "cards": [
    { "front": "What is ATP?", "back": "Adenosine Triphosphate", "hint": null }
  ],
  "created_at":  "2024-02-01T10:10:00Z"
}
```

---

### `quizzes`
```json
{
  "_id":         "quiz-uuid",
  "document_id": "uuid",
  "quiz_id":     "quiz-uuid",
  "questions": [
    {
      "id":          "q-uuid",
      "question":    "...",
      "type":        "mcq",
      "options":     [{"label":"A","text":"..."}],
      "answer":      "B",
      "explanation": "..."
    }
  ],
  "created_at":  "2024-02-01T10:15:00Z"
}
```
**Indexes:** `document_id`

---

### `study_plans`
```json
{
  "_id":           "ObjectId",
  "plan_id":       "uuid",
  "user_id":       "string",
  "document_ids":  ["uuid1"],
  "exam_date":     "2025-06-15",
  "hours_per_day": 3.0,
  "sessions": [
    {
      "date":      "2025-06-01",
      "topics":    ["Integration"],
      "duration":  3.0,
      "resources": ["Calculus.pdf"]
    }
  ],
  "created_at":    "2024-02-01T10:20:00Z"
}
```
**Indexes:** `user_id`

---

### `progress`
```json
{
  "_id":                "ObjectId",
  "user_id":            "string",
  "date":               "2024-02-01",
  "quiz_count":         2,
  "total_score":        160.0,
  "flashcards_reviewed": 25,
  "documents_read":     1,
  "study_minutes":      90,
  "chat_sessions":      3,
  "activities": [
    { "type": "quiz_completed", "details": {"score": 80}, "ts": "..." }
  ],
  "last_updated":       "2024-02-01T21:00:00Z"
}
```
**Indexes:** `(user_id, date)` descending

---

## ChromaDB Collections

One collection per uploaded document:

**Collection name:** `doc_<document_id_with_underscores>`

**Document (chunk) schema:**
```json
{
  "id":       "doc_uuid_0",
  "document": "Chunk text content...",
  "embedding": [0.123, -0.456, ...],
  "metadata": {
    "document_id":  "uuid",
    "chunk_index":  0,
    "user_id":      "user-string",
    "source_file":  "Biology Notes.pdf"
  }
}
```
**Distance metric:** Cosine similarity (`hnsw:space = cosine`)
