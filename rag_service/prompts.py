"""Prompt helpers for policy-grounded responses."""

MAX_CONTEXT_CHUNKS = 3
MAX_CHARS_PER_CHUNK = 1200

SYSTEM_PROMPT = """
You are an agency policy assistant.
Only use the provided context.
Every sentence needs citation [Policy§] or [CaseDB].
Do not include names or SSNs.
Temp=0.
""".strip()


def build_prompt(query: str, context_blocks: list[dict[str, str]]) -> str:
    """Build the final prompt from user query and retrieved policy context."""
    if context_blocks:
        limited_blocks = context_blocks[:MAX_CONTEXT_CHUNKS]
        context = "\n\n".join(
            (
                f"Source: {block.get('source', '')}\n"
                f"Section: {block.get('section', '')}\n"
                f"Text: {str(block.get('text', ''))[:MAX_CHARS_PER_CHUNK]}"
            )
            for block in limited_blocks
        )
    else:
        context = "No approved policy context was returned."

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"User question:\n{query}\n\n"
        f"Approved context:\n{context}\n\n"
        "Answer using only the approved context."
    )
