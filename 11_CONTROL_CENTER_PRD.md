# IIOS System Architecture

**Version:** 1.2.0

## Architectural position

IIOS governs all components. Models reason, Hermes executes, knowledge systems orient, Governance authorizes and Audit independently records and evaluates evidence.

```text
Owner / Control Center
        |
        v
Authority Plane: Charter + Constitution + Invariant Kernel
        |
        +--------------------+--------------------+
        |                    |                    |
        v                    v                    v
Governance/Policy      Approval Authority    Audit Authority
        |                    ^                    ^
        v                    |                    |
Orchestrator -------- approval request ---------+-- evidence/events
        |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
Intelligence Plane   Knowledge Plane     Execution Plane
Model Router         Vault + Git         Hermes + Workers
Providers             Graphify index      Sandboxed tools
        |                  |                  |
        +------------------+------------------+
                           |
                           v
Data Plane: PostgreSQL/Supabase + Object Storage + Logs + Secrets
```

Audit is not the Orchestrator's command parent. It is an independent control that receives append-oriented evidence and can request a block, escalation or kill action through Governance.

## Planes

### Authority

Charter, Constitution, ratified policies, Invariant Kernel and emergency authority. Read-only to execution runtimes.

### Governance/control

Authentication, action classification, policy evaluation, approval, capability issuance, budgets, task state and kill controls. If Governance or the Policy Engine is unavailable, Class B/C/D actions fail closed. Class A may continue only under a valid, unexpired cached policy explicitly permitting offline read-only operation.

### Intelligence

Provider-independent model registry/router. Models never enforce their own authority.

### Knowledge

- Git/Markdown: governed documents.
- Obsidian Vault: institutional knowledge and human navigation.
- Graphify: derived graph for orientation and retrieval.
- Runtime memories: advisory and profile-scoped.

### Execution

Hermes profiles/sessions/skills/cron/gateway plus deterministic workers and isolated tools.

### Data

PostgreSQL/Supabase stores tasks, policy decisions, approvals, costs and domain entities. Object storage stores large artifacts. Secret Manager stores credentials. Audit storage is append-oriented and separate from execution roles.

## Component responsibilities

### Governance API

Authenticate, classify, evaluate deterministic policy, validate budget, request approval, issue short-lived scoped capability and record the decision.

### Invariant Kernel

A versioned, schema-validated and checksum-verified policy bundle under `governance/invariant-kernel/`. It defines the non-negotiable machine-enforced baseline. Runtime agents receive read-only access and cannot ratify or rewrite it.

### Orchestrator

Decompose approved objectives, avoid duplicate work, assign execution, enforce limits and aggregate evidence. It operates only with capabilities issued by Governance.

### Audit Authority

Receive immutable events, verify policy/capability references, detect violations and request block/escalation through Governance. Execution roles cannot delete or rewrite protected records.

### Model router

Select `no_llm`, economical, standard, frontier or multi-model review using task complexity, risk, latency, sensitivity and budget. Concrete providers live in `config/model-registry.json`.

### Hermes runtime

Interactive/persistent execution, profiles, sessions, skills, cron, gateway, subagents and tool use. Sensitive capability remains behind Governance.

### Knowledge service

Index governed documents and Vault content with source IDs, timestamps, authority and sensitivity. Graph results never replace source retrieval.

## Deployment progression

1. Local: Claude Code, Obsidian, Hermes lab, Docker terminal and mock data.
2. Hybrid MVP: private VPS, Governance API, Hermes Core, database, backups and read-only connector.
3. Personal production: separated environments, egress control, dedicated audit, CI/CD approvals and tested disaster recovery.

## Technology direction

Typed frontend/backend, PostgreSQL/Supabase, Docker Compose, private networking, managed secrets and structured telemetry. Add queues, GPU or Kubernetes only from measured demand.
