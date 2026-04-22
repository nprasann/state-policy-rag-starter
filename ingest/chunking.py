"""Text chunking helpers for policy ingestion."""

import re


def is_section_header(line: str) -> bool:
    """Heuristic to detect policy section headers."""
    stripped = line.strip()
    if not stripped:
        return False

    if re.match(r"^(\d+(\.\d+)*|[A-Z]\.)\s+\S+", stripped):
        return True

    return stripped.isupper() and len(stripped.split()) <= 12


def split_text(text: str, chunk_size: int = 512, overlap: float = 0.15) -> list[str]:
    """Split text into overlapping chunks while carrying section headers forward."""
    lines = [line.strip() for line in text.splitlines()]
    overlap_tokens = max(1, int(chunk_size * overlap))
    chunks: list[str] = []
    current_header = ""
    buffer_tokens: list[str] = []

    for line in lines:
        if not line:
            continue

        if is_section_header(line):
            current_header = line
            continue

        line_tokens = line.split()
        if not line_tokens:
            continue

        if not buffer_tokens and current_header:
            buffer_tokens.extend(current_header.split())

        if len(buffer_tokens) + len(line_tokens) <= chunk_size:
            buffer_tokens.extend(line_tokens)
            continue

        if buffer_tokens:
            chunks.append(" ".join(buffer_tokens))

        retained_tokens = buffer_tokens[-overlap_tokens:] if buffer_tokens else []
        buffer_tokens = retained_tokens.copy()

        if current_header:
            header_tokens = current_header.split()
            if buffer_tokens[: len(header_tokens)] != header_tokens:
                buffer_tokens = header_tokens + buffer_tokens

        buffer_tokens.extend(line_tokens)

        while len(buffer_tokens) > chunk_size:
            chunks.append(" ".join(buffer_tokens[:chunk_size]))
            retained_tokens = buffer_tokens[chunk_size - overlap_tokens : chunk_size]
            buffer_tokens = retained_tokens + buffer_tokens[chunk_size:]
            if current_header:
                header_tokens = current_header.split()
                if buffer_tokens[: len(header_tokens)] != header_tokens:
                    buffer_tokens = header_tokens + buffer_tokens

    if buffer_tokens:
        chunks.append(" ".join(buffer_tokens))

    return chunks
