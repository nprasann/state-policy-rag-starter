"""Minimal FastAPI app so the MCP server container boots cleanly."""

from fastapi import FastAPI


app = FastAPI(title="mcp_server")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
