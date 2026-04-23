# Docs README

This guide is for an absolute beginner who wants to run `state-policy-rag-starter` on a personal computer or workstation.

It covers:

- what to install
- how to install it
- how to get the code
- how to update the code later with `git pull`
- how to start the stack
- how to ingest a policy PDF
- how to test search and RAG endpoints

macOS is the directly tested path for this repository. Windows and Linux instructions below are practical guidance and should be validated in your environment.

## 1. What This Project Needs

To run this project locally, you need:

- Git
- Docker Desktop or Docker Engine with `docker-compose`
- Python `3.10+` or `3.11`
- internet access for first-time model downloads
- a Hugging Face read token if you want smoother model downloads

Optional but recommended:

- a terminal you are comfortable using
- at least `16 GB` RAM for a better local experience
- a real PDF policy document to ingest

## 2. Fast Overview

There are two ways to get the code:

1. Clone with Git
   This is the best option if you want to update the repo later with `git pull`.

2. Download as ZIP
   This is simpler at first, but harder to keep updated.

Once the code is on your machine, the basic flow is:

1. create `.env`
2. start Docker services
3. install Python ingest dependencies
4. ingest a real policy PDF
5. test semantic search
6. test the RAG endpoint

## 3. Install Prerequisites

### Mac

Install Homebrew if needed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Install Git:

```bash
brew install git
```

Install Python:

```bash
brew install python@3.11
```

Install Docker Desktop:

- Download from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- Open Docker Desktop and wait for it to fully start

Install `docker-compose` if your machine does not already provide it:

```bash
brew install docker-compose
```

Check installs:

```bash
git --version
python3 --version
docker --version
docker-compose --version
```

### Windows

Recommended tools:

- Git for Windows: [https://git-scm.com/download/win](https://git-scm.com/download/win)
- Python `3.11`: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
- Docker Desktop: [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

During Python installation:

- enable `Add Python to PATH`

Check installs in PowerShell:

```powershell
git --version
python --version
docker --version
docker-compose --version
```

### Linux

Package names may vary by distribution, but the general pattern is:

Install Git and Python:

```bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip
```

Install Docker Engine and Docker Compose:

- Follow your distribution’s Docker installation guide, or:
- [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

Check installs:

```bash
git --version
python3 --version
docker --version
docker-compose --version
```

## 4. Get the Code

### Option A: Clone with Git

This is the recommended path.

```bash
git clone https://github.com/nprasann/state-policy-rag-starter.git
cd state-policy-rag-starter
```

To update later:

```bash
git pull origin master
```

### Option B: Download as ZIP

1. Go to the repo:
   [https://github.com/nprasann/state-policy-rag-starter](https://github.com/nprasann/state-policy-rag-starter)
2. Click `Code`
3. Click `Download ZIP`
4. Extract it
5. Open a terminal in the extracted folder

If you use the ZIP approach, there is no `git pull`. To update later, you would usually download the ZIP again.

## 5. Create the Environment File

From the project root:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Optional but recommended:

Add your Hugging Face token to `.env`:

```bash
echo 'HF_TOKEN=your_huggingface_read_token' >> .env
```

Also check these values in `.env`:

- `OLLAMA_MODEL=llama3:8b-instruct-q4_K_M`
- `EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2`
- `LLM_TEMPERATURE=0.0`

## 6. Start the Services

From the project root:

```bash
docker-compose up --build -d
```

Check status:

```bash
docker-compose ps
```

Health checks:

```bash
curl http://localhost:8080/health
curl http://localhost:8081/health
```

On Windows PowerShell, `curl` may map differently. If needed, use:

```powershell
curl.exe http://localhost:8080/health
curl.exe http://localhost:8081/health
```

## 7. Prepare Python for Ingestion

Create a virtual environment.

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r ingest/requirements.txt
```

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r ingest/requirements.txt
```

## 8. Ingest a Real Policy PDF

Use a real PDF file, not a placeholder.

### Mac / Linux

```bash
CHROMA_PORT=8001 EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2 \
python ingest/ingest.py \
  --file /full/path/to/your/policy.pdf \
  --source_name "Sample Policy" \
  --section "General"
```

### Windows PowerShell

```powershell
$env:CHROMA_PORT='8001'
$env:EMBEDDING_MODEL='sentence-transformers/all-MiniLM-L6-v2'
python ingest/ingest.py --file "C:\full\path\to\your\policy.pdf" --source_name "Sample Policy" --section "General"
```

Notes:

- quote values that contain spaces
- use straight quotes, not smart quotes
- if you change the embedding model, you must re-create the `policies` collection and re-ingest

## 9. Test Semantic Search

### Mac / Linux

```bash
curl -X POST http://localhost:8080/search_policies \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does the policy require the State Agency to display on the website home page?"}'
```

### Windows PowerShell

```powershell
curl.exe -X POST http://localhost:8080/search_policies -H "Content-Type: application/json" -H "user: test.user@state.gov" -d "{\"query\":\"What does the policy require the State Agency to display on the website home page?\"}"
```

## 10. Test the RAG Endpoint

### Mac / Linux

```bash
curl -X POST http://localhost:8081/ask \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does the policy require the State Agency to display on the website home page?"}'
```

### Windows PowerShell

```powershell
curl.exe -X POST http://localhost:8081/ask -H "Content-Type: application/json" -H "user: test.user@state.gov" -d "{\"query\":\"What does the policy require the State Agency to display on the website home page?\"}"
```

## 11. Common Commands

Start services:

```bash
docker-compose up -d
```

Rebuild and restart:

```bash
docker-compose up --build -d
```

Stop services:

```bash
docker-compose down
```

See logs:

```bash
docker-compose logs -f
```

See service-specific logs:

```bash
docker-compose logs -f mcp_server
docker-compose logs -f rag_service
docker-compose logs -f ollama
docker-compose logs -f chroma
```

Update repo if you cloned with Git:

```bash
git pull origin master
```

Check local repo status:

```bash
git status
```

## 12. Troubleshooting

### `Collection expecting embedding with dimension...`

Cause:
- you changed the embedding model after data was already stored

Fix:
- delete the `policies` collection
- re-ingest using the new embedding model

### `Collection [policies] does not exist`

Cause:
- the data has not been ingested yet into the running Chroma instance

Fix:
- run the ingest command again against `CHROMA_PORT=8001`

### `Internal Server Error` from `/ask`

Check:

```bash
docker-compose logs --tail=100 rag_service
docker-compose logs --tail=100 mcp_server
docker-compose logs --tail=100 ollama
```

### Model download is very slow

Cause:
- first-time Hugging Face model download
- missing or unauthenticated `HF_TOKEN`

Fix:
- add `HF_TOKEN` to `.env`
- retry after restarting the stack

## 13. Recommended Reading

- [README.md](../README.md)
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/DEPLOY_STATE.md](DEPLOY_STATE.md)
- [docs/SECURITY.md](SECURITY.md)
- [docs/HARDWARESETUP.md](HARDWARESETUP.md)

## 14. Final Advice

If you are brand new to this stack, start small:

1. get Docker running
2. get health checks working
3. ingest one real PDF
4. test semantic search
5. test the RAG response

Once those work, then move on to automation, better models, UI work, and production hardening.
