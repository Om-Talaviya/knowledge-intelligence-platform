# Knowledge Intelligence Platform (KIP) — Agentic Multimodal Research Platform (v2.0)

A production-grade, open-source **Agentic Multimodal Research & Knowledge Intelligence Platform** engineered for deep codebase analysis, GitHub repository ingestion, local folder indexing, visual diagram intelligence, and grounded technical research synthesis with exact citations.

---

## 🌟 Key Capabilities (v2.0 Enterprise)

- 🤖 **Autonomous Deep Research Agent**: Decomposes complex engineering questions into multi-hop sub-goals, explores AST code symbols, inspects file slices, and synthesizes grounded research dossiers.
- 🐙 **GitHub Repository Ingestion**: Shallow-clone and REST API tree ingestion for public and private repositories with branch/tag switching and commit context.
- 📁 **Local Folder & Codebase Indexer**: Recursive filesystem walker with `.gitignore` compliance, binary filtering, and batch ingestion.
- 🧩 **Language-Aware Code & AST Chunking**: Syntactic boundary chunker preserving functions, classes, and comments across Python, TypeScript, JavaScript, Go, Rust, Java, and C++.
- 🖼️ **Multimodal Visual Intelligence**: Extracts and captions system architecture diagrams, flowcharts, screenshots, and visual plots using OCR and Vision LLMs.
- 🔍 **Hybrid Retrieval with RRF**: Reciprocal Rank Fusion of dense embeddings and BM25 keyword search for robust precision across code and prose.
- 🛡️ **Zero-Hallucination Grounding & Citations**: Every sentence in synthesized research and Q&A is verified against source passages and exact file:line citations.
- ⚡ **Zero-Dependency Core**: Runs out-of-the-box offline using SQLite vector storage and deterministic hashing embeddings.

---

## 🏗️ System Architecture

```
                               ┌────────────────────────────────────────────────┐
                               │           Web UI (React 18 + Vite)             │
                               │  - Chat & Citations    - Deep Research Agent   │
                               │  - Knowledge Assets    - GitHub/Folder Ingest  │
                               └───────────────────────┬────────────────────────┘
                                                       │ REST API (FastAPI)
                               ┌───────────────────────▼────────────────────────┐
                               │             KIP Backend Services               │
                               │  - DocumentService    - GitHubIngestService    │
                               │  - IngestService      - DeepResearchAgent      │
                               └───────┬───────────────┬────────────────┬───────┘
                                       │               │                │
            ┌──────────────────────────▼───┐   ┌───────▼────────────┐   └──────────┐
            │   Hybrid Retrieval Engine    │   │  AST Code Chunker  │              │
            │  - Dense Hashing / ST Vectors│   │  - Polyglot parser │              ▼
            │  - BM25 & SQLite FTS5 Search │   │  - Symbol Extractor│     ┌─────────────────┐
            │  - Reciprocal Rank Fusion    │   └────────────────────┘     │ Multimodal Asset│
            │  - Cross-Encoder Reranker    │                              │ - Diagram OCR   │
            └──────────────┬───────────────┘                              │ - Vision LLM    │
                           │                                              └─────────────────┘
            ┌──────────────▼────────────────────────────────────────────────────┐
            │                 Grounded Evidence & Citation Gate                 │
            │      - Pre-generation gate      - Post-generation support check   │
            │      - Exact file:line tracing  - Grounding confidence score      │
            └───────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Local Development (Windows / Linux / macOS)

#### Terminal 1: Backend Server (FastAPI)
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # On Linux/macOS: source .venv/bin/activate
pip install -e .[dev]
uvicorn kip.api:app --reload --port 8000
```
> API Docs & Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Terminal 2: Frontend Workspace (React + Vite)
```powershell
cd frontend
npm install
npm run dev
```
> Frontend UI: [http://localhost:5173](http://localhost:5173)

---

### 2. Run Full Stack with Docker Compose
```bash
# Clone and enter the repository
git clone https://github.com/Om-Talaviya/knowledge-intelligence-platform.git
cd knowledge-intelligence-platform

# Copy environment template
cp .env.example .env

# Launch all services (PostgreSQL, Qdrant, Backend, Frontend)
docker compose up -d
```
> Frontend available at [http://localhost](http://localhost)

---

## 📡 API Endpoints Reference

### Autonomous Research Agent
- `POST /api/agent/research` — Executes autonomous deep research across indexed repositories and codebases.

### GitHub Repository Ingestion
- `POST /api/github/ingest` — Clones, extracts symbols, chunks, and indexes a GitHub repo.
- `GET /api/github/status/{job_id}` — Polls repository ingestion job progress.
- `POST /api/github/webhook` — Webhook listener for automated re-indexing on push events.

### Local Folder Ingestion
- `POST /api/ingest/local` — Scans and indexes a local codebase directory tree.
- `GET /api/ingest/status/{job_id}` — Polls directory ingestion progress.

### Documents & Knowledge Assets
- `POST /api/documents/upload` — Upload PDF, DOCX, Markdown, or TXT documents.
- `GET /api/documents` — List paginated documents.
- `GET /api/documents/{id}/chunks` — Inspect document chunk breakdown.
- `DELETE /api/documents/{id}` — Delete document and remove vector embeddings.

### Chat & Q&A
- `POST /api/chat/ask` — Ask a question with grounded retrieval and source citations.
- `GET /api/chat/conversations` — Retrieve conversation history.

---

## 🧪 Running Tests & Verification

```bash
# 1. Zero-dependency internal verification suite (640+ checks)
cd backend
python -m selfcheck

# 2. Pytest unit & integration test suite (90 tests)
pytest tests/ -v

# 3. Frontend linting and TypeScript compilation
cd frontend
npm run lint
npm run build
```

---

## 📄 License
MIT License.
