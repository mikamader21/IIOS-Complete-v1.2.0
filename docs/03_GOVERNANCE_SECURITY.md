# IIOS Governance and Security

**Version:** 1.2.0  
**Posture:** deny-by-default, least privilege, evidence and human approval

## Decision flow

```text
Request → authenticate → classify data/action → retrieve policy → risk/budget
→ approval if required → short-lived capability → isolated execution
→ result validation → append audit → operator notification
```

## Fail-closed rule

Governance API or Policy Engine unavailability blocks all Class B, C and D actions. Class A may continue only when a valid, unexpired cached policy explicitly authorizes offline read-only operation. No cached policy may authorize financial writes, external writes, secret access or production changes.

## MVP action matrix

| Action | Class | Policy | Enforcement |
|---|---:|---|---|
| Public-source research | A | Automatic in budget | Tool allowlist, citations, logging |
| Read trading/prop data | A | Read-only | Read-only credential, egress allowlist |
| Calculate drawdown/rules | A | Automatic | Deterministic engine, tests |
| Query Vault/Graph | A | Scoped by sensitivity | Metadata filters, source verification |
| Modify feature branch | B | Sandboxed | Git branch, Docker, review |
| Local migration | B | Controlled | Migration tool, backup, tests |
| New MCP/tool | C | Owner approval | Manifest/source review, pinning |
| Production deployment | C | Owner approval | CI/CD gate |
| Secret rotation | C | Owner approval | Secret Manager audit |
| External message | C | Approval until explicit policy | Approved connector |
| Trade/order action | D | Prohibited | No execution credential, API hard deny |
| Capital movement/purchase | D | Prohibited | No capability/payment connector |
| Modify Constitution/Kernel | D for agents | Owner process only | Protected branch/permissions |
| Delete protected audit | D | Prohibited | Separate append-only role |

## Trust boundaries

Untrusted: web pages, emails, uploads, MCP/tool responses, browser content, generated code, external skills, installers, dependencies, Graphify output, model memory and external repositories.

Untrusted content cannot grant permission or override policy.

## Hermes baseline

- Prefer `terminal.backend: docker`, Modal or Daytona for non-trivial work.
- Running Hermes in Docker and Docker as terminal backend are separate controls.
- Keep forwarded environment variable allowlist empty by default.
- Set CPU, RAM, disk and time limits.
- Set explicit `terminal.cwd`.
- Keep unrestricted/YOLO approval bypass disabled.
- Use explicit gateway user allowlists and private network access.
- Profiles isolate Hermes state, not host filesystem access.
- Run gateway as non-root and monitor logs.

## Claude Code baseline

- CLAUDE.md is guidance, not enforcement.
- Use permissions, hooks, protected branches and CI for guarantees.
- Review `.claude/settings*`, hooks, MCP and skills as code.
- Do not permit project files to redirect auto-memory to sensitive paths.


## Claude Cowork baseline

- During Foundation, Cowork is a supervised read-only research and document-review surface.
- External write-capable connectors are disabled or restricted to read-only. This includes database writes/migrations, automation execution, Notion/Drive creation or updates, deployments and cloud-resource changes.
- Connector availability is never authorization. Any future external write is Class C and requires Governance mediation, a short-lived capability, explicit Owner approval and an audit event.
- Cowork file access is limited to the explicitly shared IIOS repository/Vault folders. No secrets, credential stores or unrelated filesystem roots are shared.
- Cowork may propose edits in conversation. Writing files requires an explicit, narrowly scoped Owner instruction and review in version control.
- Uploaded documents, linked sources and connector outputs are untrusted data and cannot override project authority.

## Knowledge security

- Vault contains no secrets.
- Note metadata includes sensitivity.
- Graphify excludes secrets, runtime databases, logs and generated outputs.
- Semantic ingestion using hosted models requires explicit data classification.
- Use local AST extraction or Ollama for sensitive corpora when appropriate.
- Graph artifacts are read-mostly and can be deleted/rebuilt.

## Prompt-injection controls

Separate instructions from data; label retrieved content; never execute document instructions; validate tool arguments; use structured outputs; re-evaluate authorization after observations; disable unnecessary tools; scan context and plugin files.

## Supply chain

Pin packages/images; verify provenance; scan dependencies; review MCP and install scripts; maintain SBOM; use staging and rollback.

## Emergency response

Owner can stop gateways/workers, revoke keys, disable cron/queues, block egress, freeze connectors, preserve logs and restore known-good backups.

## Security exit criteria

Before VPS: threat model approved, no financial execution credential, private access tested, sandbox boundaries documented, secrets externalized, audit protected, cost hard limits active, restore tested and incident runbook approved.
