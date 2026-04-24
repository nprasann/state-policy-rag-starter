# Hardware Setup Guide

This guide provides hardware and infrastructure recommendations for running `state-policy-rag-starter` on Azure virtual machines or on-premises virtualized infrastructure.

The primary design goal is isolation. This workload should run in a dedicated network segment that is separated from general-purpose application servers, user workstation networks, and unrestricted internet-facing systems.

## 1. Deployment Principles

- Run the workload on dedicated infrastructure for this AI service only.
- Place all components in an isolated network zone or enclave.
- Do not co-locate the service with domain controllers, database clusters, file servers, or line-of-business application servers.
- Restrict inbound and outbound traffic to only the ports and endpoints required for operation.
- Treat the Ollama model host, Qdrant data store, and API services as sensitive systems because they may contain policy text, prompts, vectorized content, and audit logs.

## 2. Minimum Hardware Profiles

### Pilot Or Evaluation

Suitable for a single agency team, limited policy corpus, and low request volume.

- `8 vCPU`
- `32 GB RAM`
- `200 GB SSD`
- No GPU required for initial evaluation if using a smaller Ollama model such as `llama3:8b-instruct-q4_K_M`

Expected use:

- Internal pilot
- Low concurrency
- Small to medium document collection
- Manual policy ingestion

### Department Production Starter

Suitable for one department with moderate daily usage and a growing document corpus.

- `16 vCPU`
- `64 GB RAM`
- `500 GB SSD`
- Optional NVIDIA GPU with at least `16 GB VRAM` if response latency must improve or larger local models are required

Expected use:

- Moderate concurrency
- Larger policy collections
- More frequent ingestion
- Persistent audit and backup requirements

### Multi-Program Or Shared Service

Suitable for multiple programs or a centralized internal platform team.

- `24 to 32 vCPU`
- `128 GB RAM`
- `1 TB SSD` minimum
- NVIDIA GPU with `24 GB+ VRAM` strongly recommended for larger local models or higher throughput

Expected use:

- Multiple agencies or divisions
- Higher concurrency
- Separate non-production and production environments
- Centralized monitoring and backup

## 3. Azure VM Guidance

Recommended Azure-first options:

- CPU-only pilot:
  `D8as_v5` or `D8s_v5`
- Larger CPU deployment:
  `D16as_v5` or `E16as_v5`
- GPU-backed deployment:
  `NCas_T4_v3`, `NC4as_T4_v3`, or newer approved GPU VM families

Azure storage guidance:

- Use Premium SSD managed disks
- Separate OS disk from data disk where possible
- Mount data paths for:
  - `./qdrant_data`
  - `./ollama`
  - audit log export location

Azure network guidance:

- Deploy into a dedicated VNet or dedicated subnet for AI workloads
- Use NSGs to allow only approved inbound traffic
- Prefer private IP access only
- Terminate user access through VPN, ExpressRoute, Bastion, or an internal reverse proxy
- Deny direct public access to Ollama, Qdrant, and internal API ports

Recommended Azure pattern:

- One isolated resource group for the pilot
- One dedicated subnet for the workload
- One jump host or Azure Bastion for administration
- Private DNS or internal hostname registration only

## 4. On-Prem VM Guidance

Recommended virtualization platforms:

- VMware vSphere
- Hyper-V
- Nutanix AHV
- OpenShift Virtualization or KVM-based equivalents where approved

On-prem host guidance:

- Reserve CPU and memory for the AI VM where possible
- Use SSD-backed storage, not spinning disk
- Ensure backup windows do not cause storage throttling during business hours
- Keep this workload on a separate VLAN or firewall zone from shared server infrastructure

On-prem network guidance:

- Dedicated VLAN for AI workload
- Firewall policy with explicit allow rules only
- Admin access limited to jump host, bastion, or management network
- No east-west access to unrelated servers by default

## 5. Isolation And Network Segmentation

This environment should be isolated from other servers in both logical and network terms.

Required controls:

- Dedicated subnet or VLAN
- Dedicated firewall policy or NSG set
- No open inbound access from the general corporate LAN
- No internet-exposed management ports
- Allow only these trusted flows:
  - client or reverse proxy to `rag_service`
  - `rag_service` to `mcp_server`
  - `mcp_server` to Qdrant
  - `rag_service` to Ollama
  - `mcp_server` to approved case database endpoint, if used
- Deny all other east-west traffic by default

Strongly recommended:

- Separate non-production and production network segments
- Private package mirror or controlled egress path
- Egress filtering so the workload cannot freely call external SaaS endpoints
- Logging of firewall, admin, and API activity

## 6. Reuse Vs Acquire Decision

Reuse existing VM capacity only if all of the following are true:

- The host cluster is state-managed and approved for sensitive workloads
- Sufficient reserved CPU, memory, and SSD capacity exist
- A dedicated isolated subnet or VLAN can be assigned
- The workload will not share runtime with unrelated production applications
- Security can enforce restricted admin access and approved outbound traffic only

Acquire new infrastructure if any of the following apply:

- Existing clusters are shared too broadly
- GPU capacity is needed and not currently available
- Data residency or isolation controls cannot be guaranteed on current infrastructure
- The agency wants a clean production boundary for audit and procurement reasons

## 7. Storage Planning

Minimum storage areas:

- OS and container runtime
- `ollama` model storage
- `qdrant_data` vector store
- audit log retention
- backups and snapshots

Sizing notes:

- Ollama models can consume multiple gigabytes each
- Vector storage grows with document volume and embedding count
- Keep at least `30%` free disk headroom to avoid operational issues

## 8. Security Hardening Checklist

- Harden the OS using agency baseline images
- Enable disk encryption
- Patch OS and container runtime regularly
- Restrict sudo or administrative access to named administrators only
- Use MFA for bastion or remote admin access
- Forward system and container logs to an approved internal logging system
- Back up data volumes according to agency retention policy
- Scan base images and dependencies before promotion to production

## 9. Recommended Starting Architecture

For most agencies, start with one isolated Linux VM for pilot use:

- Ubuntu `22.04 LTS`
- `8 to 16 vCPU`
- `32 to 64 GB RAM`
- `200 to 500 GB Premium SSD`
- Docker and Docker Compose
- Private subnet or VLAN
- Access through internal reverse proxy, VPN, or Teams integration path only

If pilot demand grows, the next step is not usually more internet exposure. The next step is stronger separation:

- dedicated production VM or VM set
- separate non-production environment
- optional GPU-backed inference host
- tighter backup, monitoring, and admin controls

## 10. Procurement Note

For procurement and architecture review, the preferred language is:

- state-controlled hosting
- isolated network segment
- no external telemetry
- no training on agency data
- private model serving
- explicit audit logging
- allowlisted system-to-system access only
