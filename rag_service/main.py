"""FastAPI entrypoint for policy-grounded question answering."""

import os
import re
from typing import Any
from urllib import error, request

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm import generate_answer, warm_model
from prompts import build_prompt

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://mcp_server:8000")
FALLBACK_ANSWER = "I cannot find that in approved policy. Contact supervisor."
TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))

app = FastAPI(title="rag_service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    query: str


def fetch_policy_chunks(query: str, user: str | None) -> list[dict[str, str]]:
    """Call the MCP server and return the policy chunks."""
    payload = json_bytes({"query": query})
    headers = {
        "Content-Type": "application/json",
        "user": user or "",
    }
    search_request = request.Request(
        url=f"{MCP_SERVER_URL}/search_policies",
        data=payload,
        headers=headers,
        method="POST",
    )

    try:
        with request.urlopen(search_request, timeout=15) as response:
            body = response.read()
    except error.URLError:
        return []

    return json_loads(body).get("chunks", [])


def json_bytes(payload: dict[str, Any]) -> bytes:
    """Serialize a payload to UTF-8 JSON."""
    import json

    return json.dumps(payload).encode("utf-8")


def json_loads(payload: bytes) -> dict[str, Any]:
    """Deserialize a UTF-8 JSON response."""
    import json

    return json.loads(payload.decode("utf-8"))


def extract_citations(answer: str) -> list[str]:
    """Collect citations from policy or case references."""
    citations = re.findall(r"\[[^\]]+\]|§[A-Za-z0-9.\-]+|CaseDB", answer)
    seen: list[str] = []
    for citation in citations:
        if citation not in seen:
            seen.append(citation)
    return seen


@app.post("/ask")
def ask(payload: AskRequest, user: str | None = Header(default=None)) -> dict[str, Any]:
    if TEMPERATURE != 0.0:
        raise ValueError("LLM_TEMPERATURE must be 0.0")

    chunks = fetch_policy_chunks(payload.query, user)
    prompt = build_prompt(payload.query, chunks)
    answer = generate_answer(prompt)

    if "[" not in answer and "§" not in answer and "CaseDB" not in answer:
        answer = FALLBACK_ANSWER

    citations = extract_citations(answer)
    return {"answer": answer, "citations": citations}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    if TEMPERATURE != 0.0:
        raise HTTPException(status_code=503, detail="LLM_TEMPERATURE must be 0.0")

    readiness_request = request.Request(url=f"{MCP_SERVER_URL}/ready", method="GET")

    try:
        with request.urlopen(readiness_request, timeout=10) as response:
            body = response.read()
    except error.URLError as exc:
        raise HTTPException(status_code=503, detail="MCP readiness check failed") from exc

    try:
        warm_model()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Ollama readiness check failed") from exc

    return json_loads(body)
