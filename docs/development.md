# Development Guide

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm

## Backend

From the repository root:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/api/v1/health`.

## Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite prints the local URL. The frontend calls the backend through `VITE_API_BASE_URL`, which defaults to `http://127.0.0.1:8000` when unset.

## Phase 1 Boundaries

Do not add provider credentials, pretend that agents have analyzed a repository, or add a vector database as part of the foundation. New capabilities should enter through the existing interfaces and receive focused tests as they become functional.
