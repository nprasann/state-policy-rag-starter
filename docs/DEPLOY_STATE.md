# Deploy On A State VM

This guide assumes a single state-managed Linux VM for pilot deployment.

## 1. VM Spec

Recommended pilot size:

- `8 vCPU`
- `32 GB RAM`
- `200 GB SSD`
- Ubuntu `22.04 LTS`
- Outbound internet only for initial package and model download, or an approved internal mirror

If the agency plans to run larger Ollama models, increase RAM and disk accordingly.

## 2. Install Docker

Install Docker and the Compose plugin on the VM.

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin git python3 python3-pip
sudo usermod -aG docker $USER
```

Log out and back in after changing Docker group membership.

## 3. Clone The Repository

```bash
git clone <your-fork-or-repo-url>
cd state-policy-rag-starter
```

## 4. Edit `.env`

Create a local environment file and update values for the agency.

```bash
cp .env.example .env
nano .env
```

Minimum review points:

- Set `AGENCY_NAME`
- Confirm `AUTH_PROVIDER`
- Confirm `OLLAMA_MODEL`
- Confirm `ESCALATE_KEYWORDS`

## 5. Start The Stack

Build and start the services.

```bash
docker-compose up --build -d
```

Check service status:

```bash
docker-compose ps
curl http://localhost:8080/health
curl http://localhost:8081/health
```

## 6. Ingest The First Policy

Install the ingest dependencies and load a first PDF into Chroma.

```bash
python3 -m pip install -r ingest/requirements.txt
python3 ingest/ingest.py \
  --file examples/sample_policy.pdf \
  --source_name "Sample Policy" \
  --section "General"
```

## 7. Test With `curl`

Test policy retrieval through the RAG service.

```bash
curl -X POST http://localhost:8081/ask \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does policy say about removal?"}'
```

Optional direct MCP test:

```bash
curl -X POST http://localhost:8080/search_policies \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"termination of rights"}'
```

## 8. Operational Notes

- Keep the VM inside the state network or a state-approved enclave.
- Restrict inbound access to trusted users, reverse proxies, or Teams integration endpoints.
- Back up `./chroma_data` and `./ollama` according to agency retention requirements.
