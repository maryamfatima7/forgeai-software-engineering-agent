# ForgeAI

## AI-Powered Software Engineering Agent

ForgeAI is a repository-aware engineering workspace for inspecting source code, finding basic maintainability and security concerns, identifying testing gaps, understanding architecture, and asking grounded engineering questions.

This repository contains the deployable MVP. It analyzes uploaded project files without executing them and keeps repository state request-scoped, which makes the current architecture compatible with serverless deployment.

## Overview

ForgeAI accepts a project folder, selected files, or a ZIP archive in the browser. Supported text files are validated, filtered, normalized, and redacted before analysis. Deterministic analysis works without an LLM key. Copilot and implementation planning use Gemini only when `GEMINI_API_KEY` is configured.

## Features

- Repository structure scan with language, extension, size, and line metadata
- Safe upload handling with path traversal protection, limits, binary filtering, ignored directories, and secret redaction
- Python AST analysis for symbols, imports, syntax errors, TODO/FIXME markers, risky constructs, and large functions
- Lightweight JavaScript/TypeScript symbol and risky-pattern analysis
- Static heuristic security review
- Testing gap and test suggestion analysis
- Architecture and documentation suggestions based on detected files
- Lexical request-scoped retrieval for repository-aware context
- Gemini-backed copilot and implementation planning behind `LLMProvider`
- Responsive developer dashboard with loading, error, empty, and result states
- Database-backed account registration, login, logout, and HTTP-only session protection
- Railway-compatible FastAPI production server and Vercel frontend build

## Architecture

The browser sends a validated repository snapshot to the FastAPI API. Analysis services run within the request and do not execute uploaded code. The copilot path chunks the snapshot, retrieves relevant text lexically, and sends bounded, redacted context to the configured LLM provider. See [docs/architecture.md](docs/architecture.md).

## How It Works

1. Select a folder, files, or ZIP archive in the Repository view.
2. ForgeAI reads text content in the browser and sends structured file data.
3. The backend rejects unsafe paths and sensitive filenames, ignores generated directories, skips binary and oversized files, and redacts credential-like values.
4. Choose a focused workflow such as Code Analysis, Security, Tests, Architecture, or Documentation.
5. Ask Copilot a repository question when Gemini is configured.
6. Create an account or log in to access the protected dashboard and workspace APIs.

## Tech Stack

- Frontend: React, Vite, JavaScript, Tailwind CSS, Framer Motion, Lucide React, fflate
- Backend: Python, FastAPI, Pydantic Settings, Uvicorn, httpx
- AI: `LLMProvider` abstraction with Gemini REST integration
- Code intelligence: Python AST and bounded JavaScript/TypeScript heuristics
- Retrieval: request-scoped chunking and lexical retrieval
- Testing: pytest and FastAPI TestClient
- Deployment: Vercel static frontend plus Python FastAPI function

## Repository Structure

```text
ForgeAI/
├── api/index.py                 # Vercel FastAPI entrypoint
├── backend/app/
│   ├── agents/                  # Shared-provider agent routing
│   ├── api/v1/                  # Versioned API routes
│   ├── code_intelligence/       # AST and source analysis
│   ├── core/                    # Settings, errors, logging
│   ├── rag/                     # Chunking and retrieval
│   ├── repository/              # Safe request-scoped ingestion
│   ├── schemas/                 # Pydantic contracts
│   └── services/                # LLM and deterministic analysis
├── backend/tests/
├── frontend/src/                # Dashboard and API client
├── docs/                        # Architecture and deployment guides
├── vercel.json
└── requirements.txt
```

## Local Development

Prerequisites: Python 3.11+, Node.js 20+, and npm.

```powershell
# Backend
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend uses same-origin API calls by default. Vite proxies `/api` to `http://127.0.0.1:8000` during local development. For separate local servers, set `VITE_API_BASE_URL` to the backend origin in the frontend environment.

## Environment Variables

Copy `.env.example` to `.env` for local backend configuration. Never commit `.env`.

- `GEMINI_API_KEY`: required only for copilot and implementation planning
- `GEMINI_MODEL`: centralized Gemini model name
- `LLM_PROVIDER`: currently `gemini`
- `LOG_LEVEL`: backend log level
- `ALLOWED_ORIGINS`: comma-separated browser origins
- `MAX_FILE_SIZE_BYTES`, `MAX_REPOSITORY_SIZE_BYTES`, `MAX_REPOSITORY_FILES`: ingestion limits
- `VITE_API_BASE_URL`: optional frontend API origin; leave empty for same-origin Vercel deployment
- `AUTH_DATABASE_URL`: optional locally (defaults to `.forgeai_auth.db`); required as a PostgreSQL URL on Vercel
- `AUTH_SESSION_SECRET`: signing secret for HTTP-only sessions; required on Vercel
- `AUTH_COOKIE_NAME`, `AUTH_COOKIE_SECURE`, `AUTH_SESSION_MAX_AGE_SECONDS`: optional session cookie settings

## API

All functional APIs are under `/api/v1/`:

- `GET /api/health` and `GET /api/v1/health`
- `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`
- `POST /api/v1/repository/scan`
- `POST /api/v1/repository/analyze`
- `POST /api/v1/code/analyze`
- `POST /api/v1/copilot/chat`
- `POST /api/v1/security/review`
- `POST /api/v1/tests/analyze`
- `POST /api/v1/architecture/analyze`
- `POST /api/v1/documentation/generate`
- `POST /api/v1/implementation/plan`
- `GET /api/v1/project/health`

Requests use validated Pydantic models. Repository endpoints accept `{ "files": [{ "path": "...", "content": "..." }] }`.
All `/api/v1/*` workspace endpoints require an authenticated HTTP-only session cookie. Health endpoints remain public for deployment checks.

## AI Agents

The orchestrator routes `repository_analysis`, `code_analysis`, `debug`, `security`, `testing`, `documentation`, `architecture`, `copilot`, and `implementation_plan` tasks to specialized agents that share one provider abstraction and bounded repository context.

## RAG Pipeline

The MVP pipeline is: validated repository files -> text chunks -> in-memory request-scoped store -> lexical retrieval -> bounded redacted context -> Gemini. It does not claim persistent indexing or embedding-based retrieval. A managed store and embedding provider can be added later without changing the interfaces.

## Security

Uploaded repositories are untrusted input. ForgeAI never executes uploaded source, shell commands, package scripts, or binaries. It rejects traversal and sensitive filenames, skips binary content and generated directories, applies file/repository limits, redacts common credential patterns, and avoids logging secret values. The security view is a static heuristic review, not a penetration test or complete audit.

## Testing

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
cd ..\frontend
npm run build
```

## Deployment

ForgeAI deploys its FastAPI backend to Railway and its Vite frontend to Vercel. `railway.toml` starts `app.main:app` from the `backend` application directory, while `vercel.json` builds and serves `frontend`. See [docs/deployment.md](docs/deployment.md).

## Vercel Setup

1. Deploy the repository to Railway and configure the backend variables in [docs/deployment.md](docs/deployment.md).
2. Verify the Railway `/health` endpoint.
3. Import the repository into Vercel with the repository root as the project root.
4. Set `VITE_API_BASE_URL` to the Railway backend origin before the Vercel build.
5. Deploy and open the Vercel frontend.

Do not deploy automatically from this workspace.

## Limitations

- Repository state is request-scoped and is not persisted between browser reloads or serverless requests.
- Uploads are bounded by configurable limits and serverless request constraints.
- Retrieval is lexical, not embedding-based.
- Static findings require developer review and do not prove vulnerabilities.
- Gemini is optional and no AI response is available without a configured provider key.
- The MVP plans changes but does not modify, commit, clone, or execute user repositories.

## Roadmap

- Durable repository snapshots and object storage uploads
- GitHub integration with explicit authentication and read-only scopes
- Embedding provider and managed vector store
- Deeper language analysis with Tree-sitter
- Authenticated workspaces, audit events, and richer project history

## Screenshots

_Add product screenshots here as the interface evolves._

## Future Improvements

Add background indexing, incremental refresh, authenticated teams, richer source citations, and provider-independent structured generation while preserving the current safety boundary.

## License

MIT. See [LICENSE](LICENSE).
