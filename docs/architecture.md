# Architecture

ForgeAI keeps repository analysis request-scoped so the same application can run locally or as a Vercel Python function. The browser supplies a structured snapshot; the backend validates and redacts it before deterministic analysis or LLM retrieval.

## System Architecture

```mermaid
flowchart LR
    UI[React + Vite UI] --> API[FastAPI API on Vercel]
    API --> Ingest[Secure Repository Ingestion]
    API --> Router[Agent Orchestrator]
    Ingest --> Analysis[Code and Report Services]
    Router --> Agents[Specialized Agents]
    Agents --> RAG[Chunking + Lexical Retrieval]
    Agents --> Provider[LLMProvider]
    Provider --> Gemini[Gemini REST API]
```

## Repository Ingestion

```mermaid
flowchart TD
    Upload[Folder, files, or ZIP in browser] --> Structured[Structured file content]
    Structured --> Paths[Normalize relative paths]
    Paths --> Limits[Apply file and repository limits]
    Limits --> Filter[Ignore generated directories and binaries]
    Filter --> Secrets[Reject sensitive files and redact secret patterns]
    Secrets --> Snapshot[Request-scoped RepositorySnapshot]
```

The backend never executes uploaded content. The browser supports folders/files and ZIP extraction with `fflate`; the API receives only structured file content. Direct object storage uploads can be added later for larger projects.

## RAG Pipeline

```mermaid
flowchart LR
    Snapshot[RepositorySnapshot] --> Chunks[Bounded text chunks]
    Chunks --> Store[Request-scoped in-memory store]
    Store --> Retrieve[LexicalRetriever]
    Retrieve --> Context[Bounded relevant context]
    Context --> Prompt[Safe provider prompt]
```

The MVP deliberately does not claim persistent indexing, embeddings, or a vector database. `DocumentChunk`, `RepositoryIndexer`, `EmbeddingProvider`, `VectorStore`, and `Retriever` remain extension boundaries.

## Agent Orchestration

```mermaid
flowchart TD
    Task[Structured task_type] --> Orchestrator[AgentOrchestrator]
    Orchestrator --> Repo[Repository Analyzer]
    Orchestrator --> Code[Code Analyzer]
    Orchestrator --> Debug[Debugging]
    Orchestrator --> Security[Security]
    Orchestrator --> Tests[Testing]
    Orchestrator --> Docs[Documentation]
    Orchestrator --> Architecture[Architecture]
    Orchestrator --> Copilot[Engineering Copilot]
    Repo --> Provider[Shared LLMProvider]
    Code --> Provider
    Debug --> Provider
    Security --> Provider
    Tests --> Provider
    Docs --> Provider
    Architecture --> Provider
    Copilot --> Provider
```

Deterministic endpoints use local analyzers directly; generative tasks use the same provider abstraction and receive retrieved, redacted context. This avoids eight separate model implementations.

## Deployment Decision

Vercel serves the compiled frontend from `frontend/dist` and routes `/api/*` to `api/index.py`, which imports the existing FastAPI application. The API does not rely on a permanent process or global repository state. `vercel.json` intentionally uses current build/output/rewrites fields rather than the legacy `builds` configuration.
