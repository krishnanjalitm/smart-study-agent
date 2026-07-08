# API Reference — Smart Study Generator Agent

**Base URL:** `http://localhost:5000/api`

All protected endpoints require:
```
Authorization: Bearer <access_token>
```

---

## Authentication

### POST /auth/register
Create a new user account.

**Request:**
```json
{ "name": "Jane Smith", "email": "jane@example.com", "password": "secure123" }
```
**Response 201:**
```json
{
  "access_token":  "eyJ...",
  "refresh_token": "eyJ...",
  "user": { "id": "...", "name": "Jane Smith", "email": "jane@example.com" }
}
```

---

### POST /auth/login
Authenticate and receive JWT tokens.

**Request:** `{ "email": "jane@example.com", "password": "secure123" }`
**Response 200:** Same as register.

---

### POST /auth/refresh 🔒 (refresh token)
Exchange a refresh token for a new access token.

**Response:** `{ "access_token": "eyJ..." }`

---

### GET /auth/me 🔒
Return the authenticated user's profile.

---

## Documents

### POST /documents/upload 🔒
Upload a study document.

**Content-Type:** `multipart/form-data`  
**Fields:** `file` (required), `tags` (optional, comma-separated)

**Response 201:**
```json
{
  "id":            "uuid",
  "original_name": "Biology Notes.pdf",
  "file_type":     "pdf",
  "status":        "ready",
  "page_count":    12,
  "word_count":    3450,
  "tags":          ["biology"],
  "created_at":    "2024-02-01T10:00:00Z"
}
```

---

### GET /documents/ 🔒
List all documents. Query params: `page`, `per_page`, `tag`

### GET /documents/<id> 🔒
Get a single document by ID.

### DELETE /documents/<id> 🔒
Delete document, its vectors, and all generated content.

### GET /documents/search?q=<query> 🔒
Full-text search across document names and content.

---

## Summary

### POST /summary/generate 🔒
```json
{ "document_id": "uuid", "length": "short|medium|detailed" }
```
**Response:** `{ "document_id": "...", "length": "medium", "content": "...", "created_at": "..." }`

### GET /summary/<doc_id>?length=medium 🔒
Return cached summary or generate on demand.

---

## Flashcards

### POST /flashcards/generate 🔒
```json
{ "document_id": "uuid", "count": 10 }
```
**Response:**
```json
{
  "document_id": "uuid",
  "cards": [
    { "front": "What is mitosis?", "back": "Cell division producing identical cells", "hint": "Think cell cycle" }
  ],
  "created_at": "..."
}
```

### GET /flashcards/<doc_id> 🔒
Return existing flashcard set.

### POST /flashcards/reviewed 🔒
Log a study session: `{ "count": 5 }`

---

## Quiz

### POST /quiz/generate 🔒
```json
{
  "document_id":    "uuid",
  "question_types": ["mcq", "true_false"],
  "count":          10
}
```
**Response:**
```json
{
  "quiz_id": "uuid",
  "questions": [
    {
      "id": "uuid",
      "question": "Which organelle produces ATP?",
      "type": "mcq",
      "options": [{"label":"A","text":"Nucleus"}, {"label":"B","text":"Mitochondria"}, ...],
      "answer": "B",
      "explanation": "Mitochondria are known as the powerhouses of the cell."
    }
  ]
}
```

### POST /quiz/submit 🔒
```json
{ "quiz_id": "uuid", "answers": { "q_uuid": "B", "q_uuid2": "True" } }
```
**Response:** `{ "score": 80.0, "total": 10, "correct": 8, "feedback": [...] }`

### GET /quiz/history 🔒
List all quizzes taken.

---

## Planner

### POST /planner/generate 🔒
```json
{
  "document_ids":  ["uuid1", "uuid2"],
  "exam_date":     "2025-06-15",
  "hours_per_day": 3.0,
  "weak_topics":   ["Integration", "Thermodynamics"]
}
```
**Response:**
```json
{
  "plan_id": "uuid",
  "sessions": [
    { "date": "2025-06-01", "topics": ["Integration Basics"], "duration": 3.0, "resources": ["Calculus.pdf"] }
  ]
}
```

### GET /planner/ 🔒
Return the current user's study plan.

---

## Chat (RAG)

### POST /chat/ask 🔒
```json
{
  "message":      "Explain Newton's Second Law",
  "document_ids": ["uuid1"],
  "history":      [{"role":"user","content":"..."}, {"role":"assistant","content":"..."}]
}
```
**Response:**
```json
{
  "answer":  "Newton's Second Law states that F = ma...",
  "sources": [
    {
      "document_id":   "uuid",
      "document_name": "Physics Notes.pdf",
      "chunk_text":    "Force equals mass times acceleration...",
      "score":         0.94
    }
  ]
}
```

---

## Progress

### GET /progress/dashboard 🔒
Return aggregated analytics + AI-generated insights.

**Response:**
```json
{
  "avg_quiz_score":     75.5,
  "total_flashcards":   120,
  "total_documents":    8,
  "total_study_hours":  14.5,
  "study_streak":       5,
  "quiz_trend":         [{"date": "2024-02-01", "score": 70}],
  "ai_insights":        "You have been consistently improving..."
}
```

### POST /progress/log 🔒
Log a study activity manually.
```json
{ "activity_type": "document_read", "details": {"document_id": "uuid"} }
```

---

## HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created |
| 400 | Bad Request — validation error |
| 401 | Unauthorized — missing or invalid JWT |
| 404 | Not Found |
| 409 | Conflict — duplicate resource |
| 415 | Unsupported Media Type — invalid file type |
| 500 | Internal Server Error |
