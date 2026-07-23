# IIOS Project State

**Version:** 1.3.0 — Governance Core Specification (tagged, `v1.3.0` → `aa9ec6d66f4c7c84ee8218d3b5901d888086c76f`)
**Review date:** 23 July 2026
**Phase:** 2 — Autonomous Operating Layer (see `MASTER_IMPLEMENTATION_PROGRAM.md`)
**Status:** Foundation (Phase 0) and Governance Core Specification (Phase 1) complete and tagged (`v1.2.1`, `v1.3.0`). ADR-0010 and ADR-0011 are **ratified** by the Owner. Phase 2 (Autonomous Operating Layer — `OWNER_PROFILE.md`, `AUTONOMY_PROTOCOL.md`, `MASTER_IMPLEMENTATION_PROGRAM.md`, `BACKLOG.md`, the Brain/Agent/Skill/Workflow/Tool registries, memory and self-evolution protocols, `work/`) is in review.

```text
Governance Core specification: ratified
Governance Core implementation: not started
Autonomous Operating Layer: in review
```

No Governance API, Policy Engine, Approval Service, capability issuer, audit storage, or kill switch is implemented. No Brain or Agent is activated — every entry in `docs/BRAIN_REGISTRY.md` and `docs/AGENT_REGISTRY.md` is `specified`/`not_implemented`. These remain design contracts only until a separate, explicitly authorized implementation phase begins for each.

## Approved design direction proposed for ratification

- Hermes is a subordinate persistent runtime.
- Models are selected through `config/model-registry.json`; no vendor/model is constitutional.
- Obsidian is a human knowledge surface; Graphify is derived and rebuildable.
- `AGENTS.md` is the shared project instruction source; `CLAUDE.md` imports it.
- Operational state belongs in PostgreSQL/Supabase; authority remains in governed Git documents and deterministic policy.
- Financial connectors remain read-only.
- Deployment progresses local → private hybrid VPS → personal production.
- Docker Compose precedes Kubernetes.
- One governed workflow precedes persistent agent teams.
- Cowork external write connectors remain disabled/read-only until Governance mediation exists.
- The Invariant Kernel is a versioned, hashed policy bundle under `governance/invariant-kernel/`.

## Current objective

Define the documentary and operational layer (`AUTONOMY_PROTOCOL.md`, `BACKLOG.md`, `MASTER_IMPLEMENTATION_PROGRAM.md`) that lets Claude select, execute, validate, and deliver authorized work without per-file manual prompts, and specify — without activating — the Brain/Agent/Skill/Workflow architecture the rest of IIOS will be built on (`docs/BRAIN_REGISTRY.md`, `docs/AGENT_REGISTRY.md`, `docs/SKILL_CATALOG.md`, `docs/WORKFLOW_REGISTRY.md`, `docs/TOOL_REGISTRY.md`, `docs/MODEL_ROUTING.md`, `docs/MEMORY_ARCHITECTURE.md`, `docs/SELF_EVOLUTION_PROTOCOL.md`, `docs/HANDOFF_PROTOCOL.md`). No Governance API, Policy Engine, database, Hermes, executable Brain, executable Agent, connector, MCP, secret, or productive infrastructure is implemented. `BACKLOG.md`'s first `ready`-after-this-phase task is `GOV-IMP-001` (Governance Core implementation skeleton), which requires its own separate Owner authorization to begin and must not start on this phase's branch.

## Foundation acceptance criteria

- [x] Owner ratifies Master Charter and Constitution.
- [x] Owner ratifies ADR-0007, ADR-0008 and ADR-0009.
- [x] Cowork write-capable connectors are disabled or explicitly restricted to read-only.
- [x] `python scripts/verify_foundation.py` passes locally and in GitHub Actions, on both Ubuntu and Windows (v1.2.1).
- [ ] Main branch protection requires the verification workflow.
- [ ] No unresolved Critical finding remains.
- [x] Action classes and approval rules are accepted (Action Classifier + Approval Model specified, `docs/21_GOVERNANCE_CORE_SPEC.md`, `docs/24_APPROVAL_MODEL.md`; ADR-0010 ratified by Owner 23 July 2026; concrete MVP parameters ratified in ADR-0011).
- [x] Threat model and fail-closed behavior are accepted (fail-closed rule restated and applied uniformly across Governance API, Policy Engine, Capability Tokens, Audit, Kill Switch; ADR-0010 ratified by Owner 23 July 2026).
- [ ] Repository and Vault are private with independent backups.
- [ ] Secret handling and environment separation are defined.
- [x] Governance API interfaces are specified before implementation (`docs/21_GOVERNANCE_CORE_SPEC.md`, `governance/schemas/action-request.schema.json`, `governance/schemas/policy-decision.schema.json`). Governance API itself remains **not implemented**.
- [x] Audit and cost event schemas are specified before implementation (`docs/25_AUDIT_EVENT_MODEL.md`, `governance/schemas/audit-event.schema.json`; cost fields embedded in the audit event schema per `docs/12_COST_GOVERNANCE.md`). No cost/audit service implemented.
- [ ] First read-only domain is selected.

## Proposed first domain

FundingPips/prop-firm observability in read-only mode: account status, balance/equity, drawdown/rules, history, alerts and calendar; no order endpoints.

## Owner decisions still required

1. Ratify Charter, Constitution and ADR-0007/0008/0009.
2. Confirm disconnection/read-only restriction of Cowork connectors.
3. Select Supabase managed versus self-hosted PostgreSQL.
4. Select VPS provider and monthly ceiling.
5. Set daily and monthly model-cost hard limits.
6. Confirm first domain.
7. Decide Vault sync method; backup remains separate.

## Prohibited assumptions

Research cost ranges are not budgets. Runtime self-evolution is not production-approved. Graphify is not authoritative. GPU is optional. Connector availability is not permission. No autonomous financial action is authorized.
