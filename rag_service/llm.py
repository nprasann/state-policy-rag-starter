"""Ollama client helpers for the RAG service."""

import os

from ollama import Client


def get_client() -> Client:
    """Return the configured Ollama client."""
    return Client(host=os.getenv("OLLAMA_HOST", "http://ollama:11434"))


def warm_model() -> None:
    """Warm the configured Ollama model with a minimal response."""
    client = get_client()
    client.generate(
        model=os.getenv("OLLAMA_MODEL"),
        prompt="Warm up the model and reply with OK.",
        options={"temperature": 0.0, "num_predict": 1},
    )


def generate_answer(prompt: str) -> str:
    """Generate an answer from the configured Ollama model."""
    client = get_client()
    response = client.generate(
        model=os.getenv("OLLAMA_MODEL"),
        prompt=prompt,
        options={"temperature": 0.0},
    )
    return response["response"]
