"""
smart-study-agent/backend/app/models/schemas.py
Pydantic v2 schemas for request validation and response serialisation.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


# ──────────────────────────────── Auth ────────────────────────────────────────

class RegisterRequest(BaseModel):
    name:     str       = Field(..., min_length=2,  max_length=100)
    email:    EmailStr
    password: str       = Field(..., min_length=8,  max_length=128)


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    user: dict


# ──────────────────────────────── Document ────────────────────────────────────

class DocumentResponse(BaseModel):
    id:           str
    user_id:      str
    filename:     str
    original_name: str
    file_type:    str
    file_size:    int
    status:       str            # pending | processing | ready | error
    page_count:   int
    word_count:   int
    created_at:   datetime
    tags:         List[str]


# ──────────────────────────────── Summary ─────────────────────────────────────

class SummaryRequest(BaseModel):
    document_id: str
    length:      Literal["short", "medium", "detailed"] = "medium"


class SummaryResponse(BaseModel):
    document_id: str
    length:      str
    content:     str
    created_at:  datetime


# ──────────────────────────────── Flashcards ──────────────────────────────────

class FlashcardItem(BaseModel):
    front: str
    back:  str
    hint:  Optional[str] = None


class FlashcardRequest(BaseModel):
    document_id: str
    count:       int = Field(default=10, ge=1, le=50)


class FlashcardResponse(BaseModel):
    document_id: str
    cards:       List[FlashcardItem]
    created_at:  datetime


# ──────────────────────────────── Quiz ────────────────────────────────────────

class QuizOption(BaseModel):
    label:   str   # A, B, C, D
    text:    str


class QuizQuestion(BaseModel):
    id:          str
    question:    str
    type:        Literal["mcq", "true_false", "short_answer"]
    options:     Optional[List[QuizOption]] = None
    answer:      str
    explanation: Optional[str] = None


class QuizRequest(BaseModel):
    document_id: str
    question_types: List[Literal["mcq", "true_false", "short_answer"]] = ["mcq"]
    count:          int = Field(default=10, ge=1, le=30)


class QuizResponse(BaseModel):
    document_id: str
    questions:   List[QuizQuestion]
    created_at:  datetime


class QuizSubmission(BaseModel):
    quiz_id:  str
    answers:  dict   # {question_id: answer_text}


class QuizResult(BaseModel):
    quiz_id:    str
    score:      float
    total:      int
    correct:    int
    feedback:   List[dict]


# ──────────────────────────────── Study Planner ───────────────────────────────

class StudyPlanRequest(BaseModel):
    document_ids:  List[str]
    exam_date:     str          # ISO date string YYYY-MM-DD
    hours_per_day: float = Field(default=2.0, ge=0.5, le=12.0)
    weak_topics:   Optional[List[str]] = []


class StudySession(BaseModel):
    date:     str
    topics:   List[str]
    duration: float   # hours
    resources: List[str]


class StudyPlanResponse(BaseModel):
    plan_id:    str
    user_id:    str
    sessions:   List[StudySession]
    created_at: datetime


# ──────────────────────────────── Chat / RAG ──────────────────────────────────

class ChatMessage(BaseModel):
    role:    Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message:      str = Field(..., min_length=1, max_length=2000)
    document_ids: Optional[List[str]] = []
    history:      Optional[List[ChatMessage]] = []


class SourceChunk(BaseModel):
    document_id:   str
    document_name: str
    chunk_text:    str
    page_number:   Optional[int] = None
    score:         float


class ChatResponse(BaseModel):
    answer:  str
    sources: List[SourceChunk]


# ──────────────────────────────── Progress ────────────────────────────────────

class ProgressEntry(BaseModel):
    user_id:          str
    date:             str
    quiz_score:       Optional[float] = None
    documents_read:   int = 0
    flashcards_reviewed: int = 0
    study_minutes:    int = 0
    topics_covered:   List[str] = []
