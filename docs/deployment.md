# Production Deployment

## Prerequisites

- A Git provider repository containing ForgeAI
- A Vercel account for the frontend
- A Railway account for the backend
- Optional Gemini API key for Copilot and implementation planning
- A PostgreSQL-compatible database for accounts and sessions (use a Vercel Postgres or external PostgreSQL integration)
- Node.js and Python for local verification

## Repository Setup

Push the existing repository and its current history to your Git provider. Do not commit `.env`, virtual environments, `node_modules`, build output, or API keys.

## Deploy the Backend to Railway

1. Create a Railway service from this repository.
2. Railway uses `railway.toml`, or set the Start Command manually to:

```text
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT
```

3. Add the required Railway environment variables listed below.
4. Verify `https://YOUR_RAILWAY_DOMAIN/health` returns HTTP 200.

The FastAPI application import path is `app.main:app` with `backend` supplied as the application directory. Production authentication requires PostgreSQL; local SQLite is retained only for local development.

## Import the Frontend into Vercel

1. In Vercel, choose **Add New Project** and import the repository.
2. Set the Vercel project **Root Directory** to `frontend`.
3. Use Vite with build command `npm run build` and output directory `dist`.
4. The checked-in `vercel.json` is already written for that `frontend` root; do not add `frontend/` to either path.
5. Set `VITE_API_BASE_URL` to the Railway backend origin. The backend is not duplicated on Vercel.
6. Deploy only after the local checks pass.

## Environment Variables

Set these in Railway:

- `GEMINI_API_KEY`: required for AI Copilot and implementation planning
- `GEMINI_MODEL`: for example `gemini-2.0-flash`
- `LLM_PROVIDER`: `gemini`
- `ALLOWED_ORIGINS`: comma-separated frontend origins, including the Vercel production URL and local development origins
- `MAX_FILE_SIZE_BYTES`, `MAX_REPOSITORY_SIZE_BYTES`, `MAX_REPOSITORY_FILES`: optional limits
- `AUTH_DATABASE_URL`: PostgreSQL connection URL for the account store
- `AUTH_SESSION_SECRET`: long random signing secret for HTTP-only sessions
- `AUTH_COOKIE_SECURE`: set to `true` for HTTPS deployments; this enables cross-origin Vercel-to-Railway sessions
- `AUTH_COOKIE_NAME`: optional cookie name, defaults to `forgeai_session`
- `AUTH_SESSION_MAX_AGE_SECONDS`: optional session lifetime, defaults to seven days

Set this in Vercel before building:

- `VITE_API_BASE_URL`: the Railway backend origin, for example `https://forgeai-api.up.railway.app`

Vite variables are build-time values. Never expose `GEMINI_API_KEY` with a `VITE_` prefix.

## Production Verification

After deployment, verify:

```powershell
curl https://YOUR_RAILWAY_DOMAIN/health
```

Then open the deployed frontend, upload a small text repository, run Code Analysis, and confirm that the UI shows a structured result. Copilot should return a clear provider-configuration error until the Gemini key is set.

Open `/register`, create an account, refresh `/dashboard`, and confirm that the account area and protected workspace are available. `/api/v1/*` routes return `401` without the session cookie.

## Local Vercel Verification

If the Vercel CLI is available:

```powershell
npm install --global vercel
vercel dev
```

Use a local `.env` without committing it. If the CLI is unavailable, the checked-in configuration can still be validated by running the frontend build, backend tests, and the FastAPI health smoke check.

## Troubleshooting

- **404 on `/health`**: confirm the Railway service uses the checked-in `railway.toml` or the documented Start Command.
- **Frontend loads but API is unavailable**: set `VITE_API_BASE_URL` to the Railway origin and include the Vercel origin in `ALLOWED_ORIGINS`.
- **Authentication does not start on Railway**: configure both `AUTH_DATABASE_URL` and `AUTH_SESSION_SECRET`; production intentionally does not use a local SQLite file.
- **Login works locally but not after redeploy**: use one stable `AUTH_SESSION_SECRET` and a persistent PostgreSQL `AUTH_DATABASE_URL` across all deployments.
- **413 or upload rejection**: the MVP has configurable per-file, total repository, and file-count limits. Large repositories need object storage and background indexing in a later phase.
- **Copilot returns provider errors**: confirm `GEMINI_API_KEY`, `GEMINI_MODEL`, and `LLM_PROVIDER` are set in Railway Production environment variables, then redeploy.
- **Static findings look incomplete**: the MVP uses Python AST and lightweight JavaScript/TypeScript heuristics, not a full semantic analyzer.

The project is not deployed automatically by this workspace.
