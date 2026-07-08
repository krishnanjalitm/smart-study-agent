# Smart Study Generator Agent

> **IBM Agentic AI Hackathon — Problem Statement #13**
> Powered by IBM watsonx.ai · IBM Granite · IBM Langflow · LangChain · MongoDB · ChromaDB

---

## What It Does

The **Smart Study Generator Agent** is a full-stack AI application that turns raw study materials (PDFs, DOCX, TXT, images) into interactive learning tools using a Multi-Agent architecture backed by IBM Granite models.

| Feature | Description |
|---|---|
| 📄 Document Processing | Upload PDF, DOCX, TXT, PNG/JPG — text extraction + OCR |
| 🤖 RAG Q&A | Ask questions; receive cited answers from your own materials |
| 📝 AI Summaries | Short / Medium / Detailed summaries via IBM Granite |
| 🃏 Flashcards | Auto-generated question-answer cards |
| 🎯 Quiz Generator | MCQ, True/False, Short Answer with auto-grading |
| 📅 Study Planner | Personalised day-by-day schedule to your exam date |
| 📊 Progress Dashboard | Analytics + AI coaching insights |
| 🔐 JWT Auth | Secure multi-user authentication |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  React Frontend (Port 3000)              │
│  Login │ Dashboard │ Chat │ Flashcards │ Quiz │ Planner  │
└────────────────────────┬────────────────────────────────┘
                         │ REST / JSON
┌────────────────────────▼────────────────────────────────┐
│              Flask Backend (Port 5000)                   │
│  JWT Auth │ 8 API Blueprints │ Error Handling │ Logging  │
└─────┬──────────┬──────────────────────────────┬─────────┘
      │          │                              │
  MongoDB    ChromaDB                   IBM watsonx.ai
  (metadata) (vectors)                  (Granite Models)
      │          │                              │
┌─────▼──────────▼──────────────────────────────▼────────┐
│                    AI Agents Layer                       │
│  Document  │ RAG  │ Summary │ Flashcard │ Quiz │ Planner │
│  Progress  │                   IBM Langflow              │
└─────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
smart-study-agent/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # App factory
│   │   ├── agents/              # 7 AI agents
│   │   │   ├── document_agent.py
│   │   │   ├── rag_agent.py
│   │   │   ├── summary_agent.py
│   │   │   ├── flashcard_agent.py
│   │   │   ├── quiz_agent.py
│   │   │   ├── planner_agent.py
│   │   │   └── progress_agent.py
│   │   ├── api/                 # REST blueprints
│   │   │   ├── auth.py
│   │   │   ├── documents.py
│   │   │   ├── summary.py
│   │   │   ├── flashcards.py
│   │   │   ├── quiz.py
│   │   │   ├── planner.py
│   │   │   ├── progress.py
│   │   │   └── chat.py
│   │   ├── core/                # Config, logger, security
│   │   ├── db/                  # MongoDB + ChromaDB clients
│   │   ├── models/              # Pydantic schemas
│   │   ├── services/            # watsonx client, embeddings
│   │   └── utils/               # file parser, chunker, helpers
│   ├── requirements.txt
│   ├── run.py
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/               # 8 page components
│   │   ├── components/          # Layout sidebar
│   │   ├── context/             # AuthContext
│   │   └── services/            # Axios API layer
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── langflow/
│   └── smart_study_flow.json    # Langflow pipeline definition
├── tests/
│   └── backend/test_api.py
└── docker-compose.yml
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- MongoDB 7.0+
- Tesseract OCR
- IBM watsonx.ai API key + Project ID

### 1. Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your IBM watsonx.ai credentials
pip install -r requirements.txt
python run.py
```

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

### 3. Docker (recommended)

```bash
cp backend/.env.example backend/.env
# Edit backend/.env
docker-compose up --build
```

Access the app at **http://localhost:3000**

---

## Environment Variables

| Variable | Description |
|---|---|
| `WATSONX_API_KEY` | IBM watsonx.ai API key |
| `WATSONX_PROJECT_ID` | Your watsonx project GUID |
| `WATSONX_URL` | watsonx endpoint (default: us-south) |
| `GRANITE_MODEL_ID` | `ibm/granite-13b-instruct-v2` |
| `GRANITE_EMBED_MODEL` | `ibm/slate-125m-english-rtrvr` |
| `MONGO_URI` | MongoDB connection string |
| `JWT_SECRET_KEY` | Strong random string for JWT signing |

---

## AI Agents

| Agent | Trigger | Model Params |
|---|---|---|
| **Document Agent** | File upload | Chunking + embedding |
| **RAG Agent** | `/api/chat/ask` | temp=0.3, 1024 tokens |
| **Summary Agent** | `/api/summary/generate` | temp=0.5, up to 1500 tokens |
| **Flashcard Agent** | `/api/flashcards/generate` | temp=0.7, 2048 tokens |
| **Quiz Agent** | `/api/quiz/generate` | temp=0.6, 2048 tokens |
| **Planner Agent** | `/api/planner/generate` | temp=0.4, 3000 tokens |
| **Progress Agent** | `/api/progress/dashboard` | temp=0.6, 600 tokens |

---

## IBM Langflow

Import [`langflow/smart_study_flow.json`](langflow/smart_study_flow.json) into your Langflow instance (`http://localhost:7860`). The flow routes student requests to the correct IBM Granite agent based on task type.

---

## Running Tests

```bash
cd tests/backend
pip install pytest
pytest test_api.py -v
```

---

## Tech Stack

- **AI**: IBM watsonx.ai, IBM Granite 13B Instruct v2, IBM Slate-125M Embeddings
- **Orchestration**: IBM Langflow, LangChain
- **Backend**: Python 3.11, Flask 3, PyMongo, ChromaDB
- **Frontend**: React 18, TailwindCSS, Recharts, React Router
- **Storage**: MongoDB 7, ChromaDB (vector store)
- **DevOps**: Docker, Docker Compose, Gunicorn, NGINX
