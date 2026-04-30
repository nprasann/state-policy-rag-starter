# AGENTS.md

## Project Purpose
- Build a public-sector-friendly RAG starter for policy-grounded question answering.
- Keep retrieval, generation, and controlled backend access as separate concerns.
- Support local/pilot deployment with FastAPI, Qdrant, Ollama, and Docker or Podman.
- Treat this repo as a starter template, not a production-ready finished platform.

## Repository Structure
- `rag_service/`: FastAPI service for `/ask`, prompt assembly, citations, and Ollama calls.
- `mcp_server/`: FastAPI service for policy search, allowlisted SQL access, auth, and audit logging.
- `ingest/`: CLI pipeline for PDF extraction, chunking, embeddings, and Qdrant upserts.
- `docs/`: setup, architecture, deployment, security, hardware, Podman, and automation docs.
- `examples/`: sample policy PDF and SQL schema example.
- `scripts/`: local bootstrap helpers for Docker and Podman.
- `docker-compose.yml`: primary local stack.
- `docker-compose.podman.yml`: Podman override for Podman-managed volumes.
- `README.md`, `GOVERNANCE.md`, `CONTRIBUTING.md`: public-facing repo guidance.

## Architecture Rules
- Read `AGENTS.md` and `docs/sessions.md` before changing code.
- Keep `rag_service`, `mcp_server`, and ingest responsibilities separate.
- Do not collapse retrieval, SQL access, and LLM generation into one service.
- Keep `Qdrant` as the vector store unless a migration is explicitly requested.
- Keep `Ollama` as the local generation runtime unless a migration is explicitly requested.
- Preserve the public API shape unless the change is intentional and documented.
- Favor small, atomic edits over broad refactors.

## Coding Standards
- Follow the existing Python style in the repo: simple functions, clear names, short docstrings.
- Prefer minimal dependencies and minimal surface-area changes.
- Keep configuration in env vars, not hardcoded hostnames or secrets.
- Update docs when changing setup, runtime behavior, or architecture.
- Keep comments brief and only where they add real clarity.

## RAG Rules
- `LLM_TEMPERATURE` must remain deterministic for the starter path.
- Retrieval must use approved policy text from the configured Qdrant collection.
- The embedding model used for ingest and MCP search must match.
- Do not bypass citation enforcement without explicit instruction.
- Do not invent policy facts when retrieval fails; preserve fallback behavior unless intentionally changed.
- Keep chunk metadata fields compatible with current search and prompt flows.

## MCP Tool Rules
- `mcp_server` owns policy search and controlled SQL access.
- Only allow stored procedures through the explicit allowlist pattern already used in the repo.
- Do not add open-ended SQL execution.
- Preserve audit logging for MCP endpoints.
- Keep readiness tied to dependency state: embedding model loaded and vector collection available.

## Security / Secrets Rules
- Never commit secrets, tokens, `.env`, private certs, or machine-specific credentials.
- Never add real government, agency, client, or production data.
- Never add real case data, real policy records beyond safe examples, or internal-only procurement text.
- Keep sample users, hosts, and data obviously non-production.
- Treat `.env.example` as the public config reference.

## Testing / Validation Rules
- Prefer validating the smallest affected path first.
- For backend changes, use the existing health and ready endpoints:
- `http://127.0.0.1:8080/health`
- `http://127.0.0.1:8080/ready`
- `http://127.0.0.1:8081/health`
- `http://127.0.0.1:8081/ready`
- For retrieval changes, validate ingest plus `POST /search_policies`.
- For answer-path changes, validate `POST /ask`.
- If changing compose, bootstrap, or runtime behavior, verify Docker and only claim Podman support if actually tested.
- If a change affects docs or setup, update the relevant file in `docs/`.

## How Agents Should Work
- Read `AGENTS.md` and `docs/sessions.md` first.
- Check repo structure and current docs before making assumptions.
- Make one logical change at a time and verify it before moving on.
- Prefer repo-local fixes over machine-specific hacks.
- Record technical state changes in `docs/sessions.md`.
- Keep session notes factual and short: what changed, why, and what still needs validation.
- If a local-only workaround is required, call it out clearly instead of presenting it as repo truth.

## What Not To Do
- Do not commit secrets or private notes.
- Do not add real agency, client, or production data.
- Do not invent architecture features that are not present in the repo.
- Do not silently change model defaults, vector schema, or service boundaries.
- Do not mix Docker and Podman stacks on the same ports at the same time.
- Do not make broad cleanup commits unrelated to the requested task.
- Do not update `docs/sessions.md` with strategy, prompt history, or personal notes.
