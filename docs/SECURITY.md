# Security

This starter is designed to reduce common failure modes in agency-facing generative AI deployments while keeping policy and case data inside state-controlled infrastructure.

## Threat Model

### PII Leakage

Risk:
Responses may expose names, SSNs, or other sensitive identifiers through indexed content, prompts, or generated answers.

Mitigations:

- Governance requires PII stripping or masking before ingestion.
- Prompt rules prohibit names and SSNs.
- The RAG service enforces citation-based answers and falls back when grounded support is missing.
- Audit logs preserve a record of who asked what and when.

### Prompt Injection

Risk:
Injected text inside documents or user prompts could try to override policy constraints or ask the model to fabricate unsupported guidance.

Mitigations:

- The system prompt instructs the model to use only provided context.
- `LLM_TEMPERATURE` is fixed at `0.0` to reduce output variance.
- The RAG service rejects answers that do not contain approved citation markers.
- The architecture separates retrieval, prompt assembly, and generation so policy context remains explicit.

### Unauthorized SQL Access

Risk:
An agent or user could attempt open-ended SQL execution against operational systems.

Mitigations:

- The MCP server only permits stored procedures in an explicit allowlist.
- Unapproved procedure requests return `403`.
- SQL access is represented as controlled procedure calls rather than arbitrary query strings.
- All SQL requests are audit logged before returning or denying access.

## Security Controls

- MCP allowlist: only approved procedures can reach the case system.
- PII strip: documents and related records should be sanitized before indexing.
- Temperature `0.0`: model generation is fixed to deterministic behavior.
- Audit logs: each request generates a structured log entry for investigation and oversight.
- No telemetry: anonymized Chroma telemetry is disabled and hosted analytics are not assumed.

## Shared Responsibility

- State IT owns VM hardening, patching, backups, and network controls.
- Legal and Privacy teams own policy for acceptable data sources and disclosure thresholds.
- Procurement should require contractual commitments for no training, no telemetry, and in-state data handling when vendors are involved.
