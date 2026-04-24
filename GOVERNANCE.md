# Governance

This document defines operating rules for State IT, Legal, Security, and Procurement stakeholders adopting this starter.

## PII Rules With Regex

The system must not return names, SSNs, or other direct identifiers unless a formal exception is approved by the agency.

Suggested minimum detection patterns:

- SSN: `\b\d{3}-\d{2}-\d{4}\b`
- Email: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b`
- Phone: `\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b`
- DOB-like dates: `\b(?:0?[1-9]|1[0-2])[\/-](?:0?[1-9]|[12]\d|3[01])[\/-](?:19|20)\d{2}\b`
- Driver or case identifiers:
  `\b[A-Z0-9]{6,20}\b`

Operational rules:

- Strip or mask PII before indexing policy-adjacent records.
- Do not allow prompts or outputs to include names or SSNs.
- Log attempts to request restricted personal information for review.

## Citation Mandate

All response sentences must include an approved citation marker.

Approved formats:

- `[Policy§...]`
- `[CaseDB]`

If the system cannot answer with a citation grounded in approved context, it must return the escalation fallback rather than speculate.

## Audit Log Schema

Every API action should emit a structured log event with at least:

- `timestamp`
- `user`
- `action`
- `params`
- `result_count` when applicable
- `status` when applicable
- `source_system` when applicable

Recommended JSON example:

```json
{
  "timestamp": "2026-04-22T15:00:00Z",
  "user": "test.user@state.gov",
  "action": "search_policies",
  "params": {
    "query": "termination of rights",
    "result_count": 3
  }
}
```

## Human Escalation Keywords

The following terms should trigger stricter review or a supervisor handoff:

- `removal`
- `termination of rights`
- `abuse`
- `neglect`
- `emergency custody`
- `court order`
- `appeal`

Agencies may add additional keywords based on program risk and statute.

## No Training Policy

- Agency prompts, retrieved policy text, and operational case data must not be used to train foundation models.
- Fine-tuning on agency data is out of scope unless separately approved by Legal, Security, and Data Governance.
- Vendors supporting this deployment must contractually affirm that agency data is not retained for model training.

## No Telemetry

- External product telemetry must remain disabled where supported.
- The vector store and model services are self-hosted in Docker Compose without third-party telemetry enabled by default.
- No third-party analytics, prompt logging SaaS, or hosted observability tools should receive agency content unless separately approved.
