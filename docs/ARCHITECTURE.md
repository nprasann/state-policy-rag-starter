# Architecture

This document describes the runtime architecture, deployment model, core components, and key interaction flows for `state-policy-rag-starter`.

The design goal is to give State IT, Legal, Security, and Engineering teams a shared technical model for how the system operates and where governance and control points exist.

## 1. Architecture Goals

- Keep policy and prompt data inside state-controlled infrastructure
- Separate retrieval, model inference, and controlled system access
- Prevent open-ended SQL access
- Enforce citation-based responses
- Support isolated deployment on Azure or on-prem virtual machines
- Produce audit-ready request trails

## 2. High-Level Logical View

```mermaid
flowchart LR
    User["Teams / Web User"] --> RAG["rag_service<br/>FastAPI"]
    RAG --> MCP["mcp_server<br/>FastAPI"]
    MCP --> Chroma["Chroma<br/>policies collection"]
    MCP --> CaseDB["CaseDB<br/>allowlisted procedures"]
    RAG --> Ollama["Ollama<br/>local model serving"]
    Ingest["PDF Ingest CLI"] --> Chunking["Chunking + Embeddings"]
    Chunking --> Chroma
```

## 3. Deployment Diagram

The pilot deployment is intentionally simple: one isolated VM running multiple containers, with access mediated through a private network segment.

```mermaid
flowchart TB
    subgraph Agency["State Network / Isolated Segment"]
        UserZone["Teams Client or Internal Web User"]
        Proxy["Internal Reverse Proxy or VPN Entry"]

        subgraph VM["Dedicated Linux VM"]
            RAG["Container: rag_service<br/>:8081"]
            MCP["Container: mcp_server<br/>:8080"]
            CH["Container: Chroma<br/>:8001 mapped to 8000"]
            OLL["Container: Ollama<br/>:11434"]
            VOL1["Volume: ./chroma_data"]
            VOL2["Volume: ./ollama"]
        end

        DB["Approved Case Database"]
        Admin["Jump Host / Bastion"]
    end

    UserZone --> Proxy
    Proxy --> RAG
    RAG --> MCP
    RAG --> OLL
    MCP --> CH
    MCP --> DB
    CH --- VOL1
    OLL --- VOL2
    Admin --> VM
```

## 4. Network Trust Boundaries

There are three primary trust boundaries in this architecture:

1. User boundary
   External users or internal end users access the service through Teams, a web UI, or an internal reverse proxy.

2. Application boundary
   The `rag_service` and `mcp_server` containers operate as separate services so retrieval and controlled data access are not collapsed into a single runtime path.

3. Sensitive systems boundary
   Chroma, Ollama, and CaseDB hold or process sensitive content and should only be reachable from the application layer over explicitly allowed network paths.

## 5. Component Responsibilities

### rag_service

- Receives end-user questions
- Calls the MCP service for policy retrieval
- Builds the grounded prompt
- Calls Ollama with temperature fixed to `0.0`
- Enforces citation-based answer rules
- Returns the final answer and extracted citations

### mcp_server

- Provides policy search over the `policies` Chroma collection
- Provides controlled SQL access via an allowlist of stored procedures
- Resolves effective user identity
- Emits audit events for every endpoint

### Chroma

- Stores policy chunks and associated metadata
- Supports retrieval by semantic similarity
- Persists vector data on local volume storage

### Ollama

- Hosts local LLM inference
- Keeps model execution inside the agency environment
- Supports low-temperature deterministic generation

### ingest CLI

- Extracts text from PDF files
- Splits text into overlapping chunks
- Generates embeddings using `BAAI/bge-m3`
- Upserts chunk documents and metadata into Chroma

## 6. Component/Class Diagram

This is a simplified code-level view of the most important modules and their responsibilities.

```mermaid
classDiagram
    class RagMain {
      +ask(payload, user)
      +fetch_policy_chunks(query, user)
      +extract_citations(answer)
    }

    class Prompts {
      +SYSTEM_PROMPT
      +build_prompt(query, context_blocks)
    }

    class LLM {
      +generate_answer(prompt)
    }

    class MCPMain {
      +search_policies(payload, user)
      +query_sql(payload, user)
      +health(user)
      +get_chroma_collection()
    }

    class Auth {
      +get_user(token)
    }

    class Audit {
      +log(user, action, params)
    }

    class Ingest {
      +main()
      +extract_pdf_text(file_path)
      +build_record_id(source_name, section, chunk_text, index)
    }

    class Chunking {
      +split_text(text, chunk_size, overlap)
      +is_section_header(line)
    }

    RagMain --> Prompts : builds prompt
    RagMain --> LLM : calls Ollama
    RagMain --> MCPMain : HTTP search request
    MCPMain --> Auth : resolves user
    MCPMain --> Audit : logs actions
    Ingest --> Chunking : splits text
    Ingest --> Chroma : upserts chunks
```

## 7. Sequence Diagram: Question Answering Flow

This is the primary runtime path for end-user questions.

```mermaid
sequenceDiagram
    participant U as User / Teams
    participant R as rag_service
    participant M as mcp_server
    participant C as Chroma
    participant O as Ollama

    U->>R: POST /ask {query} + user header
    R->>M: POST /search_policies {query}
    M->>C: query("policies")
    C-->>M: relevant chunks + metadata
    M->>M: audit.log(user, "search_policies", ...)
    M-->>R: chunks
    R->>R: build_prompt(query, chunks)
    R->>O: generate(prompt, temperature=0.0)
    O-->>R: answer text
    R->>R: citation enforcement / fallback
    R-->>U: {answer, citations}
```

## 8. Sequence Diagram: Controlled SQL Flow

This is the protected path for case-data lookups through approved stored procedures only.

```mermaid
sequenceDiagram
    participant Caller as Trusted Caller
    participant M as mcp_server
    participant A as auth.py
    participant L as allowlist
    participant DB as CaseDB
    participant AU as audit.py

    Caller->>M: POST /query_sql {proc_name, params}
    M->>A: get_user(user header)
    A-->>M: effective user
    M->>L: validate proc_name
    alt proc is allowed
        M->>DB: execute allowlisted stored procedure
        DB-->>M: result payload
        M->>AU: log(user, "query_sql", ...)
        M-->>Caller: {data, source:"CaseDB"}
    else proc is not allowed
        M->>AU: log(user, "query_sql_denied", ...)
        M-->>Caller: HTTP 403
    end
```

## 9. Sequence Diagram: Ingestion Flow

This flow loads approved policy documents into the vector store.

```mermaid
sequenceDiagram
    participant Operator as Operator
    participant I as ingest.py
    participant PDF as pypdf
    participant CHK as chunking.py
    participant EMB as sentence-transformers
    participant C as Chroma

    Operator->>I: python ingest.py --file --source_name --section
    I->>PDF: extract text from PDF
    PDF-->>I: raw text
    I->>CHK: split_text(text, 512, 0.15)
    CHK-->>I: chunks
    I->>EMB: encode chunks with BAAI/bge-m3
    EMB-->>I: embeddings
    I->>C: upsert documents + embeddings + metadata
    C-->>I: stored successfully
    I-->>Operator: ingest summary
```

## 10. State Diagram: Question Lifecycle

This state diagram shows how a user question moves through the policy-grounded answer path.

```mermaid
stateDiagram-v2
    [*] --> Received
    Received --> RetrievingContext
    RetrievingContext --> PromptBuilt
    PromptBuilt --> ModelGenerating
    ModelGenerating --> CitationCheck
    CitationCheck --> ApprovedAnswer: citations present
    CitationCheck --> EscalationFallback: citations missing
    ApprovedAnswer --> Returned
    EscalationFallback --> Returned
    Returned --> [*]
```

## 11. State Diagram: Deployment Lifecycle

This summarizes how an agency typically moves from pilot setup to operational use.

```mermaid
stateDiagram-v2
    [*] --> Provisioned
    Provisioned --> Configured
    Configured --> ContainersStarted
    ContainersStarted --> PoliciesIngested
    PoliciesIngested --> PilotOperational
    PilotOperational --> ProductionHardened
    ProductionHardened --> Monitored
    Monitored --> [*]
```

## 12. Data Model Summary

### Policy Chunk

- `document`: chunk text
- `metadata.source`: policy or source name
- `metadata.section`: policy section
- `embedding`: semantic vector for retrieval
- `id`: deterministic record identifier

### Audit Event

- `timestamp`
- `user`
- `action`
- `params`

### SQL Request

- `proc_name`
- `params`
- `source = CaseDB`

## 13. Security-Critical Design Decisions

- Retrieval and generation are separated into distinct services
- SQL access is modeled as allowlisted procedure calls only
- Citation enforcement happens after model generation
- `LLM_TEMPERATURE` is constrained to `0.0`
- Chroma telemetry is disabled
- Audit hooks exist at the MCP service boundary

## 14. Deployment Variants

### Pilot

- Single isolated VM
- Docker Compose
- Local Chroma and Ollama volumes
- Small internal user group

### Hardened Production

- Separate non-production and production environments
- Reverse proxy or API gateway in front of `rag_service`
- Centralized log forwarding
- Backup and recovery for Chroma and Ollama volumes
- Tighter egress controls and bastion-only administration

## 15. Related Documents

- [DEPLOY_STATE.md](/Volumes/HappyFam/genai-projects/state-policy-rag-starter/docs/DEPLOY_STATE.md)
- [SECURITY.md](/Volumes/HappyFam/genai-projects/state-policy-rag-starter/docs/SECURITY.md)
- [HARDWARESETUP.md](/Volumes/HappyFam/genai-projects/state-policy-rag-starter/docs/HARDWARESETUP.md)
- [GOVERNANCE.md](/Volumes/HappyFam/genai-projects/state-policy-rag-starter/GOVERNANCE.md)
