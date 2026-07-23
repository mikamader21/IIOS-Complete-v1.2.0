# IIOS Project State

**Version:** 1.3.0 — Governance Core Specification (documentation prepared; tag not yet created — publishes only after merge, green CI, and post-merge verification)
**Review date:** 23 July 2026
**Phase:** 0 — Foundation  
**Status:** Foundation v1.2.0/v1.2.1 ratified and merged. ADR-0010 (Governance Core Boundaries) and ADR-0011 (Governance MVP Owner Decisions) are **ratified** by the Owner. The capability envelope's cryptographic profile was corrected 23 July 2026: JWS Compact Serialization, `alg: Ed25519` (RFC 9864 fully-specified identifier, not the polymorphic `EdDSA`), `kid`/`typ` mandatory in the protected header — see `docs/23_CAPABILITY_MODEL.md` and ADR-0011.

```text
Governance Core specification: ratified
Governance Core implementation: not started
```

No Governance API, Policy Engine, Approval Service, capability issuer, audit storage, or kill switch is implemented. These remain design contracts only (`docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`, `governance/schemas/`) until a separate, explicitly authorized implementation phase begins.

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

Governance Core specification is ratified (ADR-0010, ADR-0011); implementation has **not started**. `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md` and `governance/schemas/` convert the Constitution and Invariant Kernel into reviewable technical contracts (Governance API, Action Classifier, Policy Engine, Approval Service, Capability Payload/Signed Envelope, Audit Events, Kill Switch), and ADR-0011 fixes the concrete MVP parameters (idempotency window, actor authentication, Class C approval TTL, capability envelope format JWS/EdDSA/Ed25519, key custody, capability TTLs, rate limiting, Make.com classification, kill-switch drill cadence, JSON Schema validation library). No backend, database, migration, MCP, model call, connector, or infrastructure was added. Do not implement domain agents yet.

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
