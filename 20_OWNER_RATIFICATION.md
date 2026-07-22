# IIOS Control Center — Foundation PRD

**Version:** 1.2.0

## Ownership

Product owner and final operator: Owner. Claude Code builds and maintains the implementation under Governance; Hermes and other runtimes may provide telemetry but do not control approvals.

## Product objective

Give the Owner a single private surface to see what IIOS knows, decides, executes, costs and blocks.

## MVP modules

### Overview

System health, active tasks, pending approvals, cost today/month, security alerts and last backup.

### Tasks

Objective, status, assigned runtime/model, budget, evidence, retries, result and correlation ID.

### Approvals

Action class, requester, scope, risk, expiry, evidence and approve/deny. No blanket approvals.

### Audit

Searchable append-oriented events with actor, policy version, capability, tools, cost and outcome.

### Models and costs

Provider health, selected/actual model, tokens, cache, latency, task cost and budget forecast.

### Knowledge

Vault freshness, reviewed/generated note counts, graph build status, source coverage and stale nodes.

### Runtimes

Hermes profiles, gateway/cron status, sandbox health, version and blocked actions.

### Security

Credential age, egress violations, injection alerts, denied commands, dependency alerts and kill switch.

### Project state

Current phase, acceptance criteria, ADRs and next approved work.

## UX principles

Calm, high-signal, evidence-first, no decorative agent theater. Every status links to evidence. Red indicates actionable risk, not normal activity.

## Non-goals

No trading terminal, payment interface, social feed, autonomous approval or multi-tenant billing in MVP.
