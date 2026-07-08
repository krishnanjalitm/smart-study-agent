# Viva Questions & Answers
## Smart Study Generator Agent — IBM Agentic AI Hackathon

---

### Section 1: Problem & Solution Overview

**Q1. What problem does this project solve?**
> Students struggle with large volumes of study materials and inefficient study methods. This project uses AI to automatically process their materials and generate summaries, flashcards, quizzes, and personalised study plans — reducing study time while improving comprehension and retention.

**Q2. Why did you choose IBM watsonx.ai and Granite models?**
> IBM Granite models are enterprise-grade, transparent, and trained on curated educational content. watsonx.ai provides a production-ready, governed AI platform with cost controls, model versioning, and compliance — essential for an academic tool handling student data.

**Q3. What is Problem Statement #13 and how does your solution address it?**
> PS#13 asks for an AI-powered study assistant with multi-agent capabilities. Our solution implements 7 specialised agents (Document Processing, RAG, Summary, Flashcard, Quiz, Planner, Progress) orchestrated through IBM Langflow, each with a clearly defined responsibility.

---

### Section 2: RAG Pipeline

**Q4. Explain the RAG pipeline in detail.**
> 1. **Ingest:** Uploaded documents are extracted, split into 800-char overlapping chunks (150-char overlap), and embedded using IBM Slate-125M.
> 2. **Store:** Embeddings are stored in ChromaDB with cosine similarity metric, keyed by document_id.
> 3. **Retrieve:** On each question, the query is embedded and the top-5 most similar chunks are retrieved from ChromaDB.
> 4. **Generate:** Retrieved chunks + conversation history are injected into a Granite prompt template. The model generates a cited answer.

**Q5. Why use chunking instead of passing the full document?**
> LLMs have limited context windows (~4K–32K tokens). Chunking ensures we stay within limits while sending only the most *relevant* text. Overlapping chunks prevent concept fragmentation at boundaries.

**Q6. What embedding model do you use, and why?**
> IBM Slate-125M (`ibm/slate-125m-english-rtrvr`) in production — it's optimised for retrieval tasks. We fall back to `all-MiniLM-L6-v2` (sentence-transformers) in development environments where watsonx credentials aren't available.

**Q7. How do you prevent hallucinations in RAG answers?**
> Our Granite prompt explicitly instructs: "Use ONLY the context passages provided below. If the answer cannot be found, say 'I don't have enough information.'" Temperature is set to 0.3 for factual answers.

---

### Section 3: Multi-Agent Architecture

**Q8. Why use multiple agents instead of one large model?**
> Separation of concerns: each agent has a dedicated prompt, temperature, and token budget optimised for its task. A single model with a generic prompt performs worse on all tasks vs. a specialised agent per task.

**Q9. How do agents communicate in your architecture?**
> Through the Flask service layer. Each API endpoint invokes the appropriate agent function. IBM Langflow handles the visual workflow definition and can route requests between agents based on task type using a conditional router node.

**Q10. What is IBM Langflow and how is it used here?**
> Langflow is a low-code visual orchestration tool for LangChain-based pipelines. Our `smart_study_flow.json` defines the full multi-agent pipeline with nodes for embeddings, ChromaDB retrieval, and 5 Granite model agents connected through a task router.

---

### Section 4: Backend & Database

**Q11. Why Flask over FastAPI?**
> Flask is simpler for rapid hackathon development and has excellent ecosystem support. For async use cases (e.g., Celery tasks), we integrate it with Redis and Celery workers.

**Q12. Why MongoDB for metadata and ChromaDB for vectors?**
> MongoDB is schema-flexible — perfect for heterogeneous document metadata, progress records, and quiz data. ChromaDB is purpose-built for vector similarity search with efficient HNSW indexing, making it 100× faster than doing cosine similarity in MongoDB.

**Q13. How is JWT authentication implemented?**
> Flask-JWT-Extended manages token lifecycle. `access_token` expires in 15 minutes; `refresh_token` in 30 days. The React frontend automatically refreshes expired tokens via an Axios interceptor without interrupting the user.

**Q14. How is the uploaded file stored?**
> Files are saved to a UUID-named file in the `uploads/` directory (mounted as a Docker volume). Only the first 5,000 characters of extracted text are stored in MongoDB (for search/preview). Full text is chunked and stored in ChromaDB.

---

### Section 5: Frontend

**Q15. Why React with TailwindCSS?**
> React's component model makes building complex interactive UIs (flipcard animation, quiz state machine) straightforward. TailwindCSS enables rapid, consistent styling without writing custom CSS for every component.

**Q16. How does the flashcard flip animation work?**
> CSS `perspective` + `rotateY(180deg)` transform on click. The front/back faces use `backface-visibility: hidden` so only one side shows at a time. Pure CSS — no JS animation library needed.

**Q17. How does the chat maintain conversation history?**
> The last 3 turns (6 messages) are sent with each request in the `history` array. The RAG agent formats them as `User: .../Assistant: ...` text and injects it into the Granite prompt before the retrieved context.

---

### Section 6: Scalability & Production

**Q18. How would you scale this to 10,000 concurrent students?**
> 1. Replace Gunicorn workers with an async worker (Uvicorn + FastAPI migration).
> 2. Move document processing to Celery async tasks.
> 3. Add Redis caching for generated summaries.
> 4. Scale ChromaDB to Chroma Cloud or Pinecone.
> 5. Use MongoDB Atlas with read replicas.
> 6. Deploy backend on Kubernetes with HPA.

**Q19. How do you protect student data?**
> 1. JWTs with short expiry (15 min).
> 2. All DB queries filter by `user_id` — users cannot access each other's documents.
> 3. Passwords are bcrypt-hashed with a random salt.
> 4. File names are UUID-anonymised on disk.
> 5. Environment variables for all secrets (never hardcoded).

**Q20. What makes this hackathon-ready vs. a prototype?**
> Production features included: Docker Compose for one-command deployment, structured logging with loguru, Pydantic request validation, graceful error handling in all agents, NGINX reverse proxy, JWT refresh token flow, ChromaDB persistence via Docker volumes, and a comprehensive test suite.
