# Podman Support

This project supports Podman as an alternative local runtime while keeping Docker as the primary validated path.

The application code does not change between runtimes. The main differences are:

- `docker-compose` vs `podman compose`
- `podman-compose` vs delegated Docker Compose behavior
- Podman machine setup on macOS
- local networking and volume behavior
- practical validation of the Ollama container under Podman

## Support Level

Current intent:

- Docker remains the primary validated local path
- Podman is supported as an alternative runtime path
- Qdrant, `mcp_server`, and `rag_service` are expected to work well under Podman
- Ollama is the main runtime component that should always be validated in your environment

Important note:

- this repo includes Podman support scripts and docs, but Podman was not installed on the authoring machine during this update, so treat the initial Podman path as implementation-ready but not yet locally re-validated here

Validated follow-up notes from local testing:

- on macOS, `podman-compose` was a more reliable path than `podman compose`
- a normal local path such as `/Users/Shared/...` worked better than a `/Volumes/...` path for bind-mounted data directories
- Ollama required a larger Podman machine memory allocation before `/ready` succeeded

## 1. Install Podman

### macOS

Install Podman:

```bash
brew install podman
```

Initialize and start the Podman machine:

```bash
podman machine init
podman machine start
```

Confirm installation:

```bash
podman --version
podman-compose version
```

### Linux

Install Podman using your distribution package manager.

Example:

```bash
sudo apt-get update
sudo apt-get install -y podman
```

Then confirm:

```bash
podman --version
podman compose version
```

### Windows

Install Podman Desktop or Podman for Windows, then confirm:

```powershell
podman --version
podman compose version
```

## 2. Start The Stack With Podman

From the project root:

```bash
podman-compose up --build -d
```

Or use the bootstrap helper:

```bash
bash scripts/bootstrap_local_podman.sh
```

That helper will:

- start Podman services
- wait for MCP and RAG health
- ingest the sample policy if present
- wait for `/ready`

## 3. Validate The Stack

Use:

```bash
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8081/ready
```

Test search:

```bash
curl -X POST http://127.0.0.1:8080/search_policies \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does the policy require the State Agency to display on the website home page?"}'
```

Test RAG:

```bash
curl -X POST http://127.0.0.1:8081/ask \
  -H "Content-Type: application/json" \
  -H "user: test.user@state.gov" \
  -d '{"query":"What does the policy require the State Agency to display on the website home page?"}'
```

## 3A. Switching Between Docker And Podman

You can support both runtimes on the same machine, but do not run both copies of the stack at the same time.

Reason:

- both runtimes try to bind the same local ports:
  - `8080`
  - `8081`
  - `6333`
  - `11434`

If switching from Docker to Podman:

```bash
docker-compose down
podman-compose up --build -d
```

If switching from Podman back to Docker:

```bash
podman-compose down
docker-compose up --build -d
```

## 4. Notes About Ollama Under Podman

The `ollama/ollama:latest` image is a standard OCI-compatible image, so you use the same image under Podman.

What still matters:

- local CPU performance
- macOS Podman machine behavior
- model storage
- first-run model warmup latency

If the stack feels slow under Podman, check Ollama first.

## 5. Troubleshooting

### `podman compose` is not available

Check:

```bash
podman compose version
```

If unavailable, install the appropriate Podman compose support for your platform.

On macOS, `podman-compose` may be the more reliable direct command if `podman compose` tries to call Docker Compose underneath.

### The services start but local requests fail

Use `127.0.0.1` instead of `localhost`:

```bash
curl http://127.0.0.1:8080/ready
curl http://127.0.0.1:8081/ready
```

### Bind mounts fail from `/Volumes/...`

On macOS, Podman may behave better when the repo lives under a more standard local path such as:

- `/Users/Shared/...`
- a normal home-directory path

If bind mounts fail from `/Volumes/...`, copy the repo to a standard local path and retry.

### Ollama says the model requires more system memory than is available

Increase Podman machine memory.

Example:

```bash
podman machine stop
podman machine set --memory 8192 --cpus 4 podman-machine-default
podman machine start
```

If `podman machine set` is unavailable on your version, recreate the machine with higher memory.

### Ollama is very slow on first request

This can still happen under Podman, especially on CPU-only machines.

Use:

```bash
curl http://127.0.0.1:8081/ready
```

before the first real `/ask`, or use the bootstrap script which does this for you.

## 6. Operational Recommendation

If you are choosing between runtimes:

- use Docker if you want the most directly validated path today
- use Podman if your environment prefers daemonless or rootless container workflows and you are comfortable validating Ollama behavior in your target environment
