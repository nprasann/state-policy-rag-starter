"""FastAPI entrypoint for policy search and approved SQL access."""

import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

import audit
from auth import get_user

ALLOWED_PROCS = ["sp_GetCaseSummary"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
COLLECTION_NAME = os.getenv("VECTOR_COLLECTION", "policies")
_embedding_model: SentenceTransformer | None = None

app = FastAPI(title="mcp_server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchPoliciesRequest(BaseModel):
    query: str


class QuerySqlRequest(BaseModel):
    proc_name: str
    params: dict[str, Any]


def get_qdrant_client() -> QdrantClient:
    """Return the configured Qdrant client."""
    return QdrantClient(
        host=os.getenv("QDRANT_HOST", "qdrant"),
        port=int(os.getenv("QDRANT_PORT", "6333")),
    )


def collection_exists() -> bool:
    """Return True when the configured vector collection exists."""
    return get_qdrant_client().collection_exists(COLLECTION_NAME)


def get_embedding_model() -> SentenceTransformer:
    """Load the shared embedding model lazily for semantic search."""
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


@app.on_event("startup")
def preload_dependencies() -> None:
    """Warm critical dependencies before serving search requests."""
    get_embedding_model()


@app.post("/search_policies")
def search_policies(
    payload: SearchPoliciesRequest,
    user: str | None = Header(default=None),
) -> dict[str, list[dict[str, str]]]:
    resolved_user = get_user(user)
    chunks: list[dict[str, str]] = []

    try:
        client = get_qdrant_client()
        if not client.collection_exists(COLLECTION_NAME):
            raise ValueError(f"Collection [{COLLECTION_NAME}] does not exist")

        embedding_model = get_embedding_model()
        query_embedding = embedding_model.encode(payload.query).tolist()
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=3,
            with_payload=True,
        )

        for point in results.points:
            point_payload = point.payload or {}
            chunks.append(
                {
                    "text": str(point_payload.get("text", "")),
                    "source": str(point_payload.get("source", "")),
                    "section": str(point_payload.get("section", "")),
                }
            )
    except Exception as exc:
        audit.log(
            resolved_user,
            "search_policies_error",
            {"query": payload.query, "error": str(exc)},
        )
        raise HTTPException(status_code=500, detail="Policy search failed") from exc

    response = {"chunks": chunks}
    audit.log(
        resolved_user,
        "search_policies",
        {"query": payload.query, "result_count": len(chunks)},
    )
    return response


@app.post("/query_sql")
def query_sql(
    payload: QuerySqlRequest,
    user: str | None = Header(default=None),
) -> dict[str, Any]:
    resolved_user = get_user(user)

    if payload.proc_name not in ALLOWED_PROCS:
        audit.log(
            resolved_user,
            "query_sql_denied",
            {"proc_name": payload.proc_name, "params": payload.params},
        )
        raise HTTPException(status_code=403, detail="Stored procedure not allowed")

    response = {
        "data": {
            "proc_name": payload.proc_name,
            "params": payload.params,
            "status": "not_implemented",
        },
        "source": "CaseDB",
    }
    audit.log(
        resolved_user,
        "query_sql",
        {"proc_name": payload.proc_name, "params": payload.params},
    )
    return response


@app.get("/health")
def health(user: str | None = Header(default=None)) -> dict[str, str]:
    resolved_user = get_user(user)
    response = {"status": "ok"}
    audit.log(resolved_user, "health", {})
    return response


@app.get("/ready")
def ready(user: str | None = Header(default=None)) -> dict[str, str]:
    """Return readiness only when search dependencies are warmed and the collection exists."""
    resolved_user = get_user(user)

    if _embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model is not loaded")

    if not collection_exists():
        raise HTTPException(status_code=503, detail=f"Collection [{COLLECTION_NAME}] does not exist")

    audit.log(resolved_user, "ready", {"collection": COLLECTION_NAME})
    return {"status": "ready"}
