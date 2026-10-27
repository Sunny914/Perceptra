# Perceptra — Agentic RAG & Document Intelligence

Python, LangGraph, LangChain, Qdrant, Jina, FastAPI, Streamlit, Docker, NeMo Guardrails, Portkey, OpenAI, Logfire, LangSmith, Prometheus, RAGAS, PostgreSQL, Redis, GitHub Actions, AWS ECS.

- Developed an agentic retrieval-augmented generation (RAG) workflow using LangGraph to coordinate document retrieval, conditional routing, and context-grounded response generation.
- Built a document retrieval pipeline combining embeddings, Qdrant vector search, and Jina reranking to prioritize relevant evidence for user queries.
- Integrated document ingestion, chunking, and metadata handling to support knowledge retrieval across supported enterprise document formats.
- Implemented application observability, safety controls, and repeatable RAG evaluation to investigate retrieval failures and improve answer reliability.
- Packaged the FastAPI API and Streamlit UI with Docker. GitHub Actions CI lints and tests the app, and a CD workflow builds the image and deploys the API and UI to AWS ECS.

## Key Features

- **Conditional routing**: A LangGraph planner reads the conversation and either answers from history or sends a refined query through retrieval. A Postgres checkpointer keeps thread state, and falls back to in-memory state when Postgres is unavailable.
- **Guardrails**: NeMo Guardrails blocks off-topic, jailbreak, and injection inputs before any retrieval.
- **LLM gateway**: Portkey routes LLM calls through a saved config. The app calls `gpt-5-mini`; the fallback config slug is `anthropic-fallback`.
- **Retrieval**: Qdrant vector search and the Jina Reranker API (`jina-reranker-v3`). Embeddings use `jina-embeddings-v3` (1024-dim), with a local `mxbai-embed-large-v1` fallback.
- **Document parsing**: PDF, HTML, TXT, DOCX, and PPTX are parsed locally with pypdf, pdfplumber, and the office loaders.
- **Observability**: Pydantic Logfire and LangSmith traces on agent nodes, plus a Prometheus `/metrics` endpoint with RAG and guardrails counters.
- **API safety**: Optional bearer-token auth and Redis-backed or in-memory rate limiting. `/query` runs the LangGraph pipeline in the request and returns the answer.
- **Evaluation**: RAGAS pipeline with six metrics, including tool correctness, plus a Streamlit demo and `evals/run_evals.py`.
- **Delivery**: Docker Compose runs the API, UI, and Qdrant. `.github/workflows` contains CI and the ECS deployment workflow.

---

## Agent Intelligence Flow

```mermaid
graph TD
    User((User)) --> UI[Streamlit UI]
    UI --> API[FastAPI /query]
    API --> Guard{NeMo Guardrails}
    Guard -->|Blocked| UI
    Guard -->|Pass| Planner{Planner Node}
    Planner -->|Conversational| Responder[Responder Node]
    Planner -->|Technical| Retriever[Retriever Node]
    Retriever --> Reranker[Jina AI Reranker API]
    Reranker --> Responder
    Responder --> UI
    Responder -.-> Memory[(LangGraph checkpointer)]
```

---

## Project Structure

```text
├── app/
│   ├── agents/
│   │   └── nodes/       # Planner, Retriever, Responder LangGraph nodes
│   ├── gateway/         # Portkey LLM gateway — saved config, gpt-5-mini with Anthropic fallback slug
│   ├── guardrails/      # NeMo Guardrails input/output filtering
│   ├── ingestion/
│   │   ├── chunking/    # Paragraph-based text splitter (1500 char max)
│   │   └── loaders/     # Local parsers — PDF (pypdf), HTML, TXT, DOCX, PPTX
│   ├── services/
│   │   └── retrieval/   # Jina AI embeddings + Qdrant search + Jina AI reranking
│   ├── config.py        # Centralized environment variable management
│   └── main.py          # FastAPI entrypoint — guardrails gate + /query endpoint
├── evals/               # RAGAS evaluation suite + Streamlit 3-tab demo
├── ui/                  # Streamlit chat interface with reasoning step transparency
├── processed_data/      # Auto-generated — parsed & chunked JSON output per document
├── DOCS/                # Architectural and operational guides
├── DATA/                # Sample datasets (True vs Noisy documentation)
├── Dockerfile           # API and UI image used by Compose and ECS
└── requirements.txt     # Pinned dependencies
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Orchestration | LangChain + LangGraph |
| API | FastAPI |
| UI | Streamlit |
| LLMs | OpenAI `gpt-5-mini` via **Portkey**, fallback slug `anthropic-fallback` |
| Guardrails | NeMo Guardrails |
| Vector DB | Qdrant |
| Reranking | Jina AI Reranker API (`jina-reranker-v3`) |
| Embeddings | Jina AI `jina-embeddings-v3` (1024-dim) + local mxbai fallback |
| Document Parsing | pypdf, pdfplumber, python-docx, python-pptx, BeautifulSoup |
| Observability | Pydantic Logfire + LangSmith + Prometheus |
| Evaluation | RAGAS + custom Tool Correctness (Jaccard) |
| Containers | Docker and Docker Compose |
| CI/CD | GitHub Actions, Amazon ECR, Amazon ECS |

---

## Getting Started

### 1. Install dependencies

Use Python 3.12. Python 3.11 also works. Python 3.13 does not: `torch==2.5.1` has no 3.13 wheel. Dependencies are declared in `pyproject.toml` and locked in `uv.lock`.

```powershell
uv venv --python 3.12 .venv
.\.venv\Scripts\Activate.ps1
uv sync --frozen --extra dev
```

On Linux or macOS:

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv sync --frozen --extra dev
```

Add `--extra evals` when you want the RAGAS evaluation console. The API and unit tests do not need it.

### 2. Configure environment

Copy `.env.example` to `.env` and fill in real values there. Do not commit `.env`.

Required for a real query: `OPENAI_API_KEY`, `PORTKEY_API_KEY`, `PORTKEY_PRIMARY_CONFIG_ID`, `JINA_API_KEY`, and `QDRANT_URL` (or `QDRANT_CLUSTER_ENDPOINT`).

Optional: `NEON_DB_URL` (conversation memory; otherwise process-local memory that dies on restart), `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` (shared rate limits; otherwise per-process memory), `LOGFIRE_TOKEN`, `LANGSMITH_API_KEY`, `RAG_API_KEY`.

`RAG_API_KEY` is one shared demo key. It does not identify a user. Anyone who has the key and knows a `thread_id` can continue that conversation. Omit `thread_id` and the API creates a new one and returns it. There is no shared default thread.

```env
# OpenAI LLM
OPENAI_API_KEY = "..."

# LLM Gateway
PORTKEY_API_KEY = "..."

# Jina AI Embeddings + Reranker API
JINA_API_KEY = "..."

# Vector DB
QDRANT_API_KEY = "..."
QDRANT_CLUSTER_ENDPOINT = "https://your-cluster.cloud.qdrant.io:6333"

# Production persistence (Neon) & cache (Upstash Redis)
NEON_DB_URL = "postgresql://user:password@host.neon.tech/enterprise_rag?sslmode=require"
UPSTASH_REDIS_REST_URL = "https://your-db.upstash.io"
UPSTASH_REDIS_REST_TOKEN = "your-upstash-token"

# API safety
RAG_API_KEY = ""                       # set in production to require bearer auth
RATE_LIMIT_PER_MINUTE = 20

# Observability
LOGFIRE_TOKEN = "..."
LANGSMITH_API_KEY = "..."
LANGSMITH_PROJECT = "enterprise_rag"
LANGSMITH_TRACING = true
LANGSMITH_ENDPOINT = https://api.smith.langchain.com

# Evals
JUDGE_OPENAI_API_KEY = "..."

# Backend (for Streamlit UI)
BACKEND_URL = "http://localhost:8000"
```

### 3. Run data ingestion

Parses all documents in `DATA/`, chunks them, saves metadata to `processed_data/`, and indexes vectors into Qdrant. `--wipe` deletes the Qdrant collection named by `QDRANT_COLLECTION` before recreating it.

```powershell
python -m app.ingestion.processor DATA --wipe
```

> Pass `--wipe` to drop and recreate the Qdrant collection. Omit it to append to an existing collection.

### 4. Launch the app

The `/query` endpoint runs the LangGraph pipeline synchronously. You only need the FastAPI server and (optionally) the Streamlit UI. Redis and Postgres are managed by Upstash and Neon; no local persistence services are required.

> **Tip:** You can verify all external connections before starting the server:
> ```bash
> python -m app.services.health.connection_checker
> ```

```powershell
# Terminal 1 — FastAPI backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Streamlit UI
streamlit run ui/app.py
```

### 5. Query the API

```powershell
curl -X POST "http://localhost:8000/query" `
  -H "Content-Type: application/json" `
  -d '{"q": "How do I start Redis for a Kubernetes work queue?", "thread_id": "demo-7f3c1a"}'

# Response: {"question": "...", "answer": "...", "thought_process": [...], "status": "...", "sources": [...]}
```

### 6. Run the eval suite

```powershell
# Headless CLI runner (requires backend on :8000)
python -m evals.run_evals

# Or use the Streamlit demo
streamlit run evals/app.py
```

### 7. Run tests locally

```powershell
$env:LOGFIRE_IGNORE_NO_CONFIG = "1"
$env:JINA_API_KEY = "dummy"
$env:OPENAI_API_KEY = "dummy"
$env:PORTKEY_API_KEY = "dummy"
$env:PORTKEY_PRIMARY_CONFIG_ID = "pc-dummy"
$env:QDRANT_URL = "https://dummy.example.com"
uv run ruff check app tests evals
uv run ruff format --check app tests evals
uv run pytest tests/
```

---

*Perceptra — Scalable Agentic RAG & Document Intelligence.*
