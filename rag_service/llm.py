"""Ollama client helpers for the RAG service."""

import os

from ollama import Client


def generate_answer(prompt: str) -> str:
    """Generate an answer from the configured Ollama model."""
    client = Client(host=os.getenv("OLLAMA_HOST", "http://ollama:11434"))
    response = client.generate(
        model=os.getenv("OLLAMA_MODEL"),
        prompt=prompt,
        options={"temperature": 0.0},
    )
    return response["response"]
