---
name: rag-retrieval
description: Use when adding or modifying search, retrieval, ranking, context assembly, citations, or answer generation.
---

## When to Use
Use this skill when the task involves:
- Searching the vector database
- Retrieving relevant chunks
- Ranking or filtering results
- Building model context
- Returning citations
- Improving answer quality
- Adding retrieval tests

## Goal
Create a reliable retrieval flow:

user query -> query embedding -> vector search -> ranked chunks -> context assembly -> response with citations

## Required Behavior
- Retrieval must return source-backed context.
- Responses should include citations or source references when possible.
- Do not answer from the model alone when the task requires repository/document grounding.
- Keep retrieval logic separate from API/controller logic.
- Keep provider-specific code isolated behind interfaces/services.

## Search Rules
- Make top-k configurable.
- Make score threshold configurable when supported.
- Include metadata filters when useful.
- Avoid returning duplicate or near-duplicate chunks.
- Prefer precision over dumping too much context.

## Context Assembly Rules
- Include only relevant chunks.
- Preserve source labels.
- Keep context size bounded.
- Prefer concise source snippets over full document text.
- Do not expose internal metadata unless useful to the caller.

## Citation Rules
Each retrieved chunk should preserve:
- source document
- chunk id
- page/section if available
- relevance score if available

If the answer uses retrieved context, cite the source.
If retrieval produces weak evidence, say so clearly.

## Answer Generation Rules
- Keep prompts deterministic where possible.
- Use low temperature for factual/document-grounded answers.
- Tell the model to use retrieved context only.
- Tell the model not to invent unsupported facts.
- Return a useful fallback when no relevant chunks are found.

## Error Handling
- Handle empty query.
- Handle no retrieval results.
- Handle vector DB unavailable.
- Handle embedding provider failure.
- Return actionable messages for diagnostics.

## Validation
After changes, verify:
- Query returns relevant chunks.
- No-result query behaves correctly.
- Citations are returned.
- Top-k and thresholds work.
- Retrieval does not leak unrelated documents.

## Output Expectations
When completing a retrieval task, report:
- Files changed
- Retrieval behavior changed
- Config settings added/changed
- Test commands
- Example query used for validation
