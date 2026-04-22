"""FastAPI entrypoint for policy search and approved SQL access."""

import os
from typing import Any

import chromadb
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

import audit
from auth import get_user

ALLOWED_PROCS = ["sp_GetCaseSummary"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
_embedding_model: SentenceTransformer | None = None

app = FastAPI(title="mcp_server")


class SearchPoliciesRequest(BaseModel):
    query: str


class QuerySqlRequest(BaseModel):
    proc_name: str
    params: dict[str, Any]


def get_chroma_collection():
    """Return the policies collection when the Chroma server is reachable."""
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "chroma"),
        port=int(os.getenv("CHROMA_PORT", "8000")),
    )
    return client.get_collection("policies")


def get_embedding_model() -> SentenceTransformer:
    """Load the shared embedding model lazily for semantic search."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embedding_model


@app.post("/search_policies")
def search_policies(
    payload: SearchPoliciesRequest,
    user: str | None = Header(default=None),
) -> dict[str, list[dict[str, str]]]:
    resolved_user = get_user(user)
    chunks: list[dict[str, str]] = []

    try:
        collection = get_chroma_collection()
        embedding_model = get_embedding_model()
        query_embedding = embedding_model.encode([payload.query]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=5)
        documents = results.get("documents", [[]])
        metadatas = results.get("metadatas", [[]])

        for text, metadata in zip(documents[0], metadatas[0], strict=False):
            metadata = metadata or {}
            chunks.append(
                {
                    "text": text,
                    "source": str(metadata.get("source", "")),
                    "section": str(metadata.get("section", "")),
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
