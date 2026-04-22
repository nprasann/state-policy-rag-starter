# Contributing

Thanks for your interest in contributing to `state-policy-rag-starter`.

This repository is intended to be useful for State IT teams, architects, engineers, legal reviewers, procurement teams, and public-sector builders exploring responsible AI patterns. Forks, issues, pull requests, and implementation feedback are all welcome.

## What Kind Of Contributions Help Most

We especially welcome contributions in these areas:

- deployment hardening for Azure or on-prem environments
- governance and security improvements
- policy ingestion and retrieval quality
- citation enforcement and auditability
- Teams or web UI integrations
- documentation for public-sector adoption

## Before You Start

Please review:

- [README.md](README.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/SECURITY.md](docs/SECURITY.md)

For contributions that affect governance, security, or data-handling behavior, include enough explanation for technical and non-technical reviewers.

## Development Setup

1. Fork the repository.
2. Clone your fork locally.
3. Create a local environment file.

```bash
git clone <your-fork-url>
cd state-policy-rag-starter
cp .env.example .env
```

4. Start the local stack when needed.

```bash
docker-compose up --build
```

## Contribution Workflow

1. Create a branch for your change.
2. Keep the scope focused.
3. Update docs when behavior, architecture, or deployment assumptions change.
4. Run the most relevant local validation you can.
5. Open a pull request with a clear summary.

Suggested branch naming:

- `feature/<short-description>`
- `fix/<short-description>`
- `docs/<short-description>`

## Pull Request Expectations

Please include:

- what changed
- why it changed
- any impact on deployment, governance, or security
- how you tested it
- screenshots or sample requests if the change affects UI or API behavior

If your change introduces a new dependency, model, external integration, or network path, call that out explicitly.

## Design Principles

Contributions should preserve the core intent of this repo:

- keep data in state-controlled environments
- avoid open-ended SQL access
- favor deterministic behavior where possible
- preserve auditability
- prefer citation-grounded responses over speculative answers
- treat privacy, legal review, and procurement concerns as first-class design requirements

## Security And Sensitive Data

Please do not:

- commit secrets, tokens, or internal credentials
- commit real case data or sensitive documents
- add telemetry or third-party tracking without clear justification
- expand SQL access beyond explicit allowlists without documenting the risk and review model

If you discover a security issue, avoid opening a public issue with exploit details. Share a minimal report and enough detail to reproduce safely.

## Documentation Contributions

Documentation improvements are absolutely welcome. In many public-sector settings, strong docs are as important as code.

Helpful documentation areas include:

- hardware sizing
- network isolation patterns
- procurement language
- security review checklists
- public-sector deployment examples

## Feedback From Agencies And Practitioners

Even if you are not submitting code, feedback is valuable.

Useful examples:

- what blocked adoption
- what a state review board asked for
- what deployment constraints mattered most
- what governance questions came up first

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 license used by this repository.

If this project is useful to you, feel free to fork it, open issues, suggest improvements, and share what would make it more practical in real-world public sector environments.
