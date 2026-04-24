# state-policy-rag-starter

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-starter-success)
![MCP](https://img.shields.io/badge/MCP-server-purple)
![RAG](https://img.shields.io/badge/AI-RAG-orange)
![Ollama](https://img.shields.io/badge/LLM-Ollama-black)
![Vector%20DB](https://img.shields.io/badge/vector%20db-Qdrant-c2185b)

`state-policy-rag-starter` is a starter repository for a retrieval-augmented generation workflow that helps state agencies answer policy questions using approved policy text and tightly scoped case data access.

## What It Does

- Ingests policy PDFs into a Qdrant vector store.
- Exposes an MCP service for policy search and a strict SQL stored procedure allowlist.
- Runs a RAG service that only answers from approved context and requires citations.
- Uses Ollama for in-state model serving so policy and case data do not leave state-controlled infrastructure.
- Provides a starter governance, deployment, and security package for State IT, Legal, and Procurement teams.

## Why This Starter

- Cost target: less than `$15K` for a starter deployment on a single state-managed VM plus implementation time.
- Data stays in-state: documents, vectors, prompts, and generated answers stay on infrastructure operated by or for the agency.
- Procurement-ready framing: see [Security](docs/SECURITY.md), [Deployment](docs/DEPLOY_STATE.md), [Architecture](docs/ARCHITECTURE.md), and [Hardware Setup](docs/HARDWARESETUP.md).

## Featured In

- Medium: [The Problem With Most AI Demos and Why I Built a Public-Sector RAG Starter Instead](https://medium.com/@nprasann/the-problem-with-most-ai-demos-and-why-i-built-a-public-sector-rag-starter-instead-95be0db949af)

## Implemented Features

- Core project scaffolding and Docker-based service configuration for local and pilot deployments
- RAG service implementation with strict temperature control and citation enforcement
- MCP server integration supporting policy search, SQL whitelisting, and audit logging
- Dedicated ingestion pipeline for extracting, chunking, embedding, and indexing policy documents

## Model Usage

This project uses two different model roles:

- Embedding model: used for ingestion and MCP semantic search
- Generation model: used for final answer generation in the RAG service

Current local development defaults:

- Hugging Face embedding model: `sentence-transformers/all-MiniLM-L6-v2`
- Ollama generation model: `llama3:8b-instruct-q4_K_M`

Why this separation matters:

- the embedding model converts policy text and user queries into vectors for semantic retrieval
- the Ollama model generates the final answer from the retrieved policy context
- the ingest embedding model and MCP search embedding model must match, or the vector collection will reject the embeddings because of dimension mismatch

For higher-quality production retrieval, the repository also supports larger embedding models such as `BAAI/bge-m3`, but the smaller MiniLM model provides a faster and more practical local developer experience

## Container Runtime Support

This starter supports:

- Docker as the primary validated local path
- Podman as an alternative local runtime path

Quick links:

- [Setup Guide](docs/SETUP_GUIDE.md)
- [Podman Guide](docs/PODMAN.md)

Runtime switching note:

- Do not run Docker and Podman copies of this stack at the same time on one machine because they compete for the same ports
- If you switch runtimes, bring the current stack down first, then start the other one

## 5-Minute Quickstart

macOS is the directly tested local path for this repository. Windows and Linux quickstart instructions below are AI-assisted guidance and should be validated in your environment before production use.

<details open>
<summary><strong>Mac</strong></summary>

1. Clone the repository and enter it.

```bash
git clone <your-fork-or-repo-url>
cd state-policy-rag-starter
```

2. Create a local environment file.

```bash
cp .env.example .env
```

3. For local development, set a Hugging Face read token in `.env` if model downloads are needed.

```bash
echo 'HF_TOKEN=your_huggingface_read_token' >> .env
```

4. Start the stack.

```bash
docker-compose up --build
```

Optional faster bootstrap:

```bash
bash scripts/bootstrap_local.sh
```

Optional Podman bootstrap:

```bash
bash scripts/bootstrap_local_podman.sh
```

If you switch back to Docker after using Podman:

```bash
podman-compose down
docker-compose up --build
```

5. In a second shell, install ingest dependencies if needed and ingest a first policy PDF.

```bash
python3 -m pip install -r ingest/requirements.txt
QDRANT_PORT=6333 EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
python3 ingest/ingest.py \
  --file examples/sample_policy.pdf \
  --source_name "Sample Policy" \
  --section "General"
```

6. Test semantic search.

```bash
curl -X POST http://localhost:8080/search_policies \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does the policy require the State Agency to display on the website home page?"}'
```

7. Test the RAG endpoint.

```bash
curl -X POST http://localhost:8081/ask \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does policy say about termination of rights?"}'
```

If you hit setup or runtime issues during quickstart, see the [Beginner Setup Guide](docs/SETUP_GUIDE.md), especially the troubleshooting section with copy-paste recovery commands.

Local networking note:

- If `localhost` behaves inconsistently on macOS, use `127.0.0.1` for local health, search, and RAG checks instead.

</details>

<details>
<summary><strong>Windows</strong></summary>

These steps are AI-assisted guidance. Validate locally before wider rollout.

1. Clone the repository and enter it in PowerShell.

```powershell
git clone <your-fork-or-repo-url>
cd state-policy-rag-starter
```

2. Create a local environment file.

```powershell
Copy-Item .env.example .env
```

3. Add a Hugging Face read token to `.env` if model downloads are needed.

```powershell
Add-Content .env 'HF_TOKEN=your_huggingface_read_token'
```

4. Start the stack.

```powershell
docker-compose up --build
```

5. Create a virtual environment, install ingest dependencies, and ingest a policy PDF.

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r ingest/requirements.txt
$env:QDRANT_PORT='6333'
$env:EMBEDDING_MODEL='sentence-transformers/all-MiniLM-L6-v2'
python ingest/ingest.py --file examples/sample_policy.pdf --source_name "Sample Policy" --section "General"
```

6. Test semantic search.

```powershell
curl.exe -X POST http://localhost:8080/search_policies -H "Content-Type: application/json" -H "user: test.user@state.gov" -d "{\"query\":\"What does the policy require the State Agency to display on the website home page?\"}"
```

7. Test the RAG endpoint.

```powershell
curl.exe -X POST http://localhost:8081/ask -H "Content-Type: application/json" -H "user: test.user@state.gov" -d "{\"query\":\"What does policy say about termination of rights?\"}"
```

</details>

<details>
<summary><strong>Linux</strong></summary>

These steps are AI-assisted guidance. Validate locally before wider rollout.

1. Clone the repository and enter it.

```bash
git clone <your-fork-or-repo-url>
cd state-policy-rag-starter
```

2. Create a local environment file.

```bash
cp .env.example .env
```

3. Add a Hugging Face read token to `.env` if model downloads are needed.

```bash
echo 'HF_TOKEN=your_huggingface_read_token' >> .env
```

4. Start the stack.

```bash
docker-compose up --build
```

5. Create a virtual environment, install ingest dependencies, and ingest a policy PDF.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r ingest/requirements.txt
QDRANT_PORT=6333 EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
python3 ingest/ingest.py \
  --file examples/sample_policy.pdf \
  --source_name "Sample Policy" \
  --section "General"
```

6. Test semantic search.

```bash
curl -X POST http://localhost:8080/search_policies \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does the policy require the State Agency to display on the website home page?"}'
```

7. Test the RAG endpoint.

```bash
curl -X POST http://localhost:8081/ask \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does policy say about termination of rights?"}'
```

</details>

## Architecture

```mermaid
flowchart LR
    A["Teams or Web Client"] --> B["rag_service<br/>FastAPI"]
    B --> C["mcp_server<br/>FastAPI"]
    C --> D["Qdrant<br/>policies collection"]
    C --> E["CaseDB<br/>allowed procedures only"]
    B --> F["Ollama<br/>local model serving"]
    G["Policy PDF Ingest"] --> H["sentence-transformers<br/>BAAI/bge-m3"]
    H --> D
```

## Repo Map

- [README.md](README.md): project overview and quickstart
- [GOVERNANCE.md](GOVERNANCE.md): usage, privacy, citation, and audit requirements
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): runtime topology, diagrams, trust boundaries, and request flows
- [docs/HARDWARESETUP.md](docs/HARDWARESETUP.md): hardware sizing and isolated network guidance for Azure or on-prem
- [docs/SECURITY.md](docs/SECURITY.md): threat model and technical controls
- [docs/DEPLOY_STATE.md](docs/DEPLOY_STATE.md): step-by-step single-VM deployment guide
- [docs/AUTOMATED_INGESTION.md](docs/AUTOMATED_INGESTION.md): ETL design for scheduled policy refresh and vector synchronization
- [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md): beginner-friendly setup and run guide for Mac, Windows, and Linux
- [docs/PODMAN.md](docs/PODMAN.md): Podman runtime setup and validation guidance

## Deployment Planning Docs

- [Architecture Guide](docs/ARCHITECTURE.md) for deployment, sequence, class, and state diagrams
- [Hardware Setup Guide](docs/HARDWARESETUP.md) for VM sizing, storage, and network isolation recommendations
- [Security Guide](docs/SECURITY.md) for threat model and mitigations
- [State Deployment Guide](docs/DEPLOY_STATE.md) for pilot rollout steps
- [Automated Ingestion Guide](docs/AUTOMATED_INGESTION.md) for the planned scheduled refresh pipeline

## Local Development Notes

- `docker-compose` is the validated local command path for this repo
- local ingest writes to host-exposed Qdrant on port `6333`
- the ingest embedding model and MCP search embedding model must match
- if you change `EMBEDDING_MODEL`, delete and recreate the `policies` collection before re-ingesting
- `HF_TOKEN` helps avoid slow or rate-limited Hugging Face downloads during first-time model setup
- `bash scripts/bootstrap_local.sh` is the fastest way to warm the services, ingest a sample policy, and wait for `/ready`

## Future Roadmap

- Advanced Semantic Search: improve retrieval precision with re-ranking models layered on top of vector search
- Automated Data Refresh: move from manual ingestion to a scheduled and repeatable pipeline
- Expanded Policy Coverage: support additional policy formats such as HTML and DOCX alongside PDF
- Enhanced UI/UX: develop a dedicated frontend for policy exploration and guided question workflows

## Open Source And Feedback

This repository is meant to be open and practical.

- Feel free to fork it for your own agency, internal prototype, or public-sector adaptation
- Feedback is welcome from State IT, architects, legal teams, security reviewers, and builders working on responsible AI
- Issues, suggestions, and improvements are all useful, especially around governance, deployment, and in-state operating models

## Intended Outcome

This starter is designed for agencies that need a practical path to policy-grounded assistance without sending protected data to external hosted LLM services and without allowing open-ended SQL access.

If this repository is useful, please consider forking it, sharing feedback, and giving it a star on GitHub.
