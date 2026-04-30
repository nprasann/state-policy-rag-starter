---
name: rag-ingestion
description: Use when adding or modifying document loading, chunking, metadata extraction, embedding, or vector indexing.
---

## When to Use
Use this skill when the task involves:
- Loading documents such as PDF, Markdown, TXT, HTML, or structured files
- Splitting documents into chunks
- Creating embeddings
- Writing chunks and metadata to a vector database
- Rebuilding or refreshing an index
- Adding ingestion validation or logging

## Goal
Create a predictable ingestion pipeline:

source document -> loader -> normalized text -> chunks -> embeddings -> vector store

## Required Behavior
- Preserve source traceability for every chunk.
- Store metadata with each chunk:
  - source file or URI
  - document title when available
  - chunk id
  - page number or section when available
  - ingestion timestamp when appropriate
- Avoid duplicate indexing when possible.
- Handle unsupported files gracefully.
- Log ingestion summary:
  - documents processed
  - chunks created
  - failures
  - skipped files

## Chunking Rules
- Prefer semantic or section-aware chunking when practical.
- Use fixed-size chunking only as a fallback.
- Keep chunk size configurable.
- Keep overlap configurable.
- Avoid chunks so large that retrieval becomes noisy.
- Avoid chunks so small that context becomes fragmented.

## Embedding Rules
- Do not hardcode embedding model names.
- Read provider/model settings from configuration.
- Keep embedding generation isolated behind a service/interface.
- Make it possible to swap embedding providers later.
- Do not store secrets in source code.

## Vector Store Rules
- Store chunk text and metadata together.
- Use deterministic ids when practical.
- Ensure re-ingestion can update or replace existing chunks.
- Keep vector DB client code isolated.
- Do not spread vector DB calls across unrelated layers.

## Error Handling
- A single bad document should not crash the whole ingestion job.
- Return or log actionable errors.
- Include filename/source in errors.
- Fail fast only for configuration or infrastructure errors.

## Validation
After changes, verify:
- A small sample document can be ingested.
- Expected number of chunks are created.
- Metadata is stored.
- Retrieval can find at least one ingested chunk.
- Re-running ingestion does not create uncontrolled duplicates.

## Output Expectations
When completing an ingestion task, report:
- Files changed
- Configuration added/changed
- How to run ingestion
- How to validate results
- Known limitations
