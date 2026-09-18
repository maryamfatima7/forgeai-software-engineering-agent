# ForgeAI

ForgeAI is an AI-powered software engineering platform foundation. It is designed to help developers understand repositories, investigate defects, review security, generate tests and documentation, and work with an engineering-focused copilot.

## Problem Statement

Modern software repositories are difficult to understand and maintain across code, architecture, tests, documentation, and operational context. ForgeAI will bring those signals into a repository-aware engineering workspace instead of treating development work as a generic chat experience.

## Planned Capabilities

- Repository understanding and semantic code search
- Code analysis, bug detection, and debugging assistance
- Architecture and security reviews
- Test and documentation generation
- Repository-aware AI chat and implementation planning
- Project health reports

## Technology Stack

- Frontend: React, Vite, JavaScript, Tailwind CSS, Framer Motion, Lucide React
- Backend: Python, FastAPI, Pydantic Settings, Uvicorn
- AI: Provider abstraction with Gemini planned as the initial provider
- Code intelligence: Python AST foundation, with Git and Tree-sitter planned later
- Testing: pytest for the backend and Vitest when frontend behavior requires it

## Architecture Overview

The frontend communicates with a versioned FastAPI API. The API will later delegate requests to an orchestrator, specialized agents, code intelligence services, and retrieval components. LLM and vector-store integrations are deliberately abstracted so providers can evolve independently. See [docs/architecture.md](docs/architecture.md).

## Project Structure

```text
ForgeAI/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── api/v1/
│   │   ├── code_intelligence/
│   │   ├── core/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/api/
│   ├── src/App.jsx
│   └── package.json
├── docs/
├── .env.example
├── .gitignore
└── LICENSE
```

## Local Development

Backend:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://127.0.0.1:8000` for the backend. Set `VITE_API_BASE_URL` to change it.

## Environment Variables

Copy `.env.example` to `.env` for local configuration:

- `GEMINI_API_KEY`: reserved for a future Gemini integration; leave empty in Phase 1
- `LLM_PROVIDER`: provider name, currently defaulting to `gemini`
- `LOG_LEVEL`: backend log level
- `VITE_API_BASE_URL`: frontend API origin

## Current Development Phase

Phase 1 is the engineering foundation only. The health endpoint and dashboard shell are functional. Agents, LLM calls, repository ingestion, retrieval, and analysis are interfaces or honest empty states, not simulated product functionality.

## Roadmap

1. Phase 1: project foundation, API health, dashboard shell, and extension points
2. Phase 2: repository connection and safe repository ingestion
3. Phase 3: code intelligence and retrieval foundations
4. Phase 4: provider-backed agent workflows
5. Phase 5: production hardening, observability, and deployment

## Security Notes

- Never commit `.env` or real credentials.
- API keys are intentionally not used in Phase 1.
- Repository access and tool execution will require explicit boundaries and validation in later phases.
- Do not treat generated analysis as authoritative without developer review.
