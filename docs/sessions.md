# Sessions

## Purpose
- Starter repo for policy-grounded RAG using local model serving and a vector database.
- Separate retrieval, answer generation, and controlled backend access into distinct services.
- Provide a local and pilot-friendly runtime using FastAPI, Qdrant, Ollama, and container orchestration.
- Include public setup, security, deployment, and governance guidance for future extension.

## Architecture Snapshot
- Main components:
  - `rag_service`: `/ask`, prompt assembly, citation extraction, Ollama calls.
  - `mcp_server`: `/search_policies`, `/query_sql`, auth resolution, audit logging, readiness checks.
  - `ingest`: PDF extraction, chunking, embeddings, Qdrant upsert CLI.
  - `qdrant`: vector store for policy chunks.
  - `ollama`: local generation runtime.
- High-level data flow:
  - PDF -> `ingest/ingest.py` -> embeddings -> Qdrant `policies` collection.
  - User query -> `rag_service` -> `mcp_server` policy search -> Qdrant chunks -> Ollama answer -> citations/fallback.
  - Optional SQL path stays behind the MCP allowlist.
- Runtime model:
  - Primary local runtime: Docker Compose.
  - Alternate runtime: Podman with a compose override.
  - Default local validation uses `127.0.0.1` on ports `8080`, `8081`, `6333`, and `11434`.

## Current Implemented State
- Existing folders/files:
  - `rag_service/`, `mcp_server/`, `ingest/`, `docs/`, `examples/`, `scripts/`.
  - `docker-compose.yml` for the main stack.
  - `docker-compose.podman.yml` for Podman volume overrides.
  - `README.md`, `GOVERNANCE.md`, `CONTRIBUTING.md`.
- Working features:
  - Qdrant-backed policy ingest and semantic search.
  - MCP readiness and health endpoints.
  - RAG readiness and answer path with citation extraction and fallback behavior.
  - Docker local flow validated.
  - Podman local flow validated in this clone with external-backed Podman machine storage.
- Known assumptions:
  - Ingest embedding model must match the MCP search embedding model.
  - `LLM_TEMPERATURE` is expected to stay deterministic for the starter path.
  - Search depends on a populated `policies` collection.
  - Ollama answer latency may be high on first warmup or on CPU-only local runs.
  - This clone currently includes local Podman/runtime adjustments not yet assumed to be published.

## Open Work / Next Steps
- Confirm whether the current Podman support changes should remain local-only or be committed.
- Normalize Podman documentation if external-backed runtime support is intended to be public.
- Add lightweight automated validation for `/ready`, ingest, and `/search_policies`.
- Improve answer quality and retrieval ranking separately from runtime work.
- Keep `docs/sessions.md` append-only for future technical handoffs.

## Decisions
- Qdrant is the active vector database for this repo.
- Ollama is the active local generation runtime for this repo.
- `rag_service`, `mcp_server`, and ingest remain separate responsibilities.
- Podman uses `docker-compose.podman.yml` to shift service data to Podman-managed volumes.
- Local validation should prefer `127.0.0.1` if `localhost` is inconsistent.

## Session Log
- Date: 2026-04-30
- Summary:
  - Added `AGENTS.md` at repo root.
  - Replaced the placeholder session template with this technical handoff file.
  - Validated local Podman runtime in this clone using an external-backed Podman machine and Podman-managed volumes.
  - Validated MCP health and policy search after re-ingest with the matching embedding model.
  - Validated RAG readiness and `/ask` after seeding existing Ollama model files into the new Podman-backed runtime.
- Decisions:
  - Keep session notes short, technical, and append-only.
  - Treat external-backed Podman support as current local technical state in this clone.
  - Preserve the current service boundaries and Qdrant/Ollama architecture.
- Files modified:
  - `AGENTS.md`
  - `docs/sessions.md`
  - Local runtime-related files observed in the clone: `docker-compose.podman.yml`, `scripts/bootstrap_local_podman.sh`, `mcp_server/Dockerfile`, `rag_service/Dockerfile`
- Validation:
  - `mcp_server /health` and `/ready` returned healthy after startup.
  - Sample policy ingest completed successfully after using the matching embedding model.
  - `POST /search_policies` returned policy chunks from Qdrant.
  - `rag_service /ready` returned ready after Ollama warmup/model seeding.
  - `POST /ask` returned an answer payload with citations.
