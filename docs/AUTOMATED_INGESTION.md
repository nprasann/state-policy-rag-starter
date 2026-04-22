# Automated Ingestion Pipeline

This document describes the planned automated ingestion pipeline for keeping policy content in the RAG system current without requiring manual refresh steps.

## I. Objective

Automate the ingestion of new or updated state policy documents so the RAG system can serve current policy guidance with minimal operational overhead.

## II. System Architecture

The pipeline follows an ETL pattern adapted for policy retrieval and LLM grounding.

### 1. Extraction: Source Monitor

The pipeline begins with a scheduled monitor that checks a source repository, storage location, or approved directory for new or updated policy files.

Recommended trigger options:

- GitHub Actions for repository-hosted policy sources
- AWS Lambda or Azure Functions for cloud storage or scheduled polling
- Cron on a state-managed VM for simple isolated deployments

Recommended change-detection approach:

- compute a file hash such as `MD5` or `SHA-256`
- compare the current hash to the last processed hash
- process only new or modified files

This reduces unnecessary re-embedding and avoids duplicate document processing.

### 2. Transformation: Processing

After change detection, the pipeline extracts text and converts source documents into retrieval-ready chunks.

Recommended processing stages:

- parse PDF files with `pypdf` for simple workflows
- use `LlamaParse` or an equivalent higher-accuracy parser where layout fidelity is important
- split text with recursive chunking
- preserve overlap to maintain policy context across chunk boundaries
- enrich each chunk with metadata to improve retrieval filtering and citation quality

Suggested chunking baseline:

- chunk size: `1000` tokens
- overlap: `100` tokens

Recommended metadata fields:

- `source_url`
- `policy_date`
- `department`
- `source_name`
- `section`
- `document_hash`

### 3. Loading: Vector Sync

Once processing is complete, embeddings are generated and synchronized into the vector database.

Recommended loading behavior:

- generate embeddings with `sentence-transformers` or the approved local embedding model
- upsert into the Chroma `policies` collection
- update vectors for modified documents
- insert vectors for newly detected documents
- optionally remove or mark archived content if the source policy was withdrawn

Upsert is preferred over blind insert because it keeps the vector store aligned with current source material.

## III. Key Technical Components

### Orchestration

Recommended options:

- `GitHub Actions` for repository-based policy content
- `Airflow` for enterprise-scale pipelines with multiple sources and stronger scheduling needs
- `Cron` for smaller isolated deployments

### Storage

The pipeline uses the existing Chroma vector store and its `policies` collection.

### Validation

After each refresh cycle, the pipeline should run a basic sanity check against the RAG service.

Example validation prompt:

`What is the latest policy version?`

The goal is not perfect semantic validation in Phase 1. The goal is to confirm that the most recent content is retrievable after the refresh.

## IV. Implementation Plan

### Phase 1: Delta Check Logic

- implement source scanning and file hash comparison
- persist the last processed hash set
- identify only new or modified files for downstream processing

### Phase 2: Containerized Ingestion

- package the automated ingestion job into the existing Docker environment
- align dependencies with the current ingest runtime
- support execution in the same isolated environment as the rest of the stack

### Phase 3: Audit Logging

- add structured audit events for each refresh cycle
- record which policies were added, updated, skipped, or failed
- track refresh timestamps and processing outcomes

## Recommended Future Enhancements

- re-ranking models for higher retrieval precision after vector search
- source connectors for HTML and DOCX policy content
- scheduled archival handling for superseded policy versions
- dashboard or UI status view for ingestion health and last refresh time

## Operational Notes

- keep the refresh pipeline inside the same state-controlled network boundary as the main stack
- restrict source access to approved repositories or storage locations only
- do not enable third-party telemetry in the refresh workflow
- log failures clearly so operations teams can identify partial refresh issues

## Relationship To Existing Components

- `ingest/ingest.py` provides the current manual ingestion baseline
- `ingest/chunking.py` provides the initial chunking logic
- Chroma remains the vector storage target
- the RAG service remains the consumer of refreshed policy content

This document is a design and planning artifact for the next stage of ingestion automation rather than a description of functionality already shipped.
