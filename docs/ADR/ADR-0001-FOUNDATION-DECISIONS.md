# ADR-0001 — Foundation Decisions

Status: Proposed  
Date: 21 July 2026

- IIOS governs all runtimes and models.
- AGENTS.md is shared operational source; CLAUDE.md imports it.
- Hermes reference baseline v0.18.2; production pins tested version.
- Git/Markdown stores authority; database stores operations; Secret Manager stores credentials.
- Financial MVP is read-only.
- Docker/Modal/Daytona isolates non-trivial command execution.
- Docker Compose first; no mandatory GPU or Kubernetes.
- Agent growth follows measured need.
