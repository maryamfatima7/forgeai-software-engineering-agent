# Development Guide

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- npm

## Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

The local health endpoint is `http://127.0.0.1:8000/api/health`.

## Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Leave `VITE_API_BASE_URL` empty for same-origin deployment. For separate local servers, set it to `http://127.0.0.1:8000`.

## Functional Workflow

1. Open the Repository view.
2. Choose a project folder, source files, or a ZIP archive.
3. Confirm the file summary and indexed file list.
4. Run Code Analysis, Security, Tests, Architecture, or Documentation.
5. Configure `GEMINI_API_KEY` before using AI Copilot or Implementation Planning.

Uploaded code is never executed. Analysis is request-scoped and disappears when the browser state or serverless request ends.

## Quality Checks

```powershell
cd backend
.venv\Scripts\python.exe -m pytest
cd ..\frontend
npm run build
```

## Environment Variables

See the root `.env.example`. The backend reads its values from `.env`; Vite reads variables prefixed with `VITE_` at build time.
