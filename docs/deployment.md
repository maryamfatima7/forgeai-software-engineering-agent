# Vercel Deployment

## Prerequisites

- A Git provider repository containing ForgeAI
- A Vercel account
- Optional Gemini API key for Copilot and implementation planning
- A PostgreSQL-compatible database for accounts and sessions (use a Vercel Postgres or external PostgreSQL integration)
- Node.js and Python for local verification

## Repository Setup

Push the existing repository and its current history to your Git provider. Do not commit `.env`, virtual environments, `node_modules`, build output, or API keys.

## Import into Vercel

1. In Vercel, choose **Add New Project** and import the repository.
2. Keep the project root at the ForgeAI repository root.
3. Do not override the detected framework with a second frontend project.
4. The checked-in `vercel.json` runs `npm --prefix frontend run build`, publishes `frontend/dist`, and rewrites `/api/*` to the FastAPI function at `api/index.py`.
5. Deploy only after the local checks pass.

## Environment Variables

Set these in the Vercel project settings:

- `GEMINI_API_KEY`: required for AI Copilot and implementation planning
- `GEMINI_MODEL`: for example `gemini-2.0-flash`
- `LLM_PROVIDER`: `gemini`
- `ALLOWED_ORIGINS`: the deployed origin if cross-origin access is needed
- `MAX_FILE_SIZE_BYTES`, `MAX_REPOSITORY_SIZE_BYTES`, `MAX_REPOSITORY_FILES`: optional limits
- `VITE_API_BASE_URL`: leave empty when frontend and API share the Vercel origin
- `AUTH_DATABASE_URL`: PostgreSQL connection URL for the account store; required in Vercel
- `AUTH_SESSION_SECRET`: long random signing secret for HTTP-only sessions; required in Vercel
- `AUTH_COOKIE_SECURE`: set to `true` in Vercel HTTPS deployments
- `AUTH_COOKIE_NAME`: optional cookie name, defaults to `forgeai_session`
- `AUTH_SESSION_MAX_AGE_SECONDS`: optional session lifetime, defaults to seven days

Vite variables are build-time values. Never expose `GEMINI_API_KEY` with a `VITE_` prefix.

## Production Verification

After deployment, verify:

```powershell
curl https://YOUR_DOMAIN.vercel.app/api/health
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

- **404 on `/api/health`**: confirm the Vercel project root is the repository root and `api/index.py` is present.
- **Frontend loads but API is unavailable**: leave `VITE_API_BASE_URL` empty for same-origin routing, or set it to the correct API origin and include that origin in `ALLOWED_ORIGINS`.
- **Authentication does not start on Vercel**: configure both `AUTH_DATABASE_URL` and `AUTH_SESSION_SECRET`; the deployment intentionally does not use a local SQLite file.
- **Login works locally but not after redeploy**: use one stable `AUTH_SESSION_SECRET` and a persistent PostgreSQL `AUTH_DATABASE_URL` across all deployments.
- **413 or upload rejection**: the MVP has configurable per-file, total repository, and file-count limits. Large repositories need object storage and background indexing in a later phase.
- **Copilot returns provider errors**: confirm `GEMINI_API_KEY`, `GEMINI_MODEL`, and `LLM_PROVIDER` are set in Vercel Production environment variables, then redeploy.
- **Static findings look incomplete**: the MVP uses Python AST and lightweight JavaScript/TypeScript heuristics, not a full semantic analyzer.

The project is not deployed automatically by this workspace.
