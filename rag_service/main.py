"""Minimal FastAPI app so the RAG service container boots cleanly."""

from fastapi import FastAPI


app = FastAPI(title="rag_service")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
