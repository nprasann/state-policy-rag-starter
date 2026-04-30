---
name: python-fastapi-notes
description: Repo-specific implementation guidance for the Python FastAPI RAG starter.
---

## When to Use
Use alongside a shared skill when working in the Python RAG repo.

## Stack Assumptions
- Python
- FastAPI service layer
- RAG service module
- MCP server module
- Vector DB client such as Qdrant or Chroma
- Configuration via environment variables or settings module

## Implementation Rules
- Keep API routes thin.
- Put business logic in services.
- Put vector DB calls behind a client or repository abstraction.
- Put embedding provider calls behind a provider abstraction.
- Keep ingestion, retrieval, and generation separately testable.
- Avoid importing framework-specific objects deep into business logic.
- Use type hints for public functions.

## Suggested Layering
- API/routes: request/response only
- Services: ingestion/retrieval workflows
- Providers: embedding/model integrations
- Repositories/clients: vector DB access
- Models/schemas: typed request/response objects
- Tests: unit tests for services, integration tests for API/vector DB

## Validation
Prefer:
- pytest for unit tests
- FastAPI TestClient for endpoint tests
- small fixture documents for ingestion tests
- environment-driven config for provider/vector DB tests
