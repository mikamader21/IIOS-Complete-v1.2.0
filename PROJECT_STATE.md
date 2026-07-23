# IIOS Project State

**Version:** 1.3.0 — Governance Core Specification (tagged, `v1.3.0` → `aa9ec6d66f4c7c84ee8218d3b5901d888086c76f`); Governance Core implementation skeleton in review
**Review date:** 23 July 2026
**Phase:** 3 — Governance Core Implementation (see `MASTER_IMPLEMENTATION_PROGRAM.md`)
**Status:** Foundation (Phase 0), Governance Core Specification (Phase 1), and Autonomous Operating Layer (Phase 2) complete. Phase 2 merged (PR #6, commit `83c2c73`, merge commit `1f4ea9762cb5a2060cc38746af057c63ef2286a7`). ADR-0010 and ADR-0011 are **ratified**; ADR-0012 (policy bundle format) is **Proposed**. Phase 3's first task, `GOV-IMP-001` (Governance Core implementation skeleton — local, deterministic, in-memory reference implementation), is in review on `feature/governance-core-skeleton`, explicitly authorized by the Owner for skeleton scope only.

```text
Governance Core specification: ratified
Governance Core implementation skeleton: in review
Governance Core production implementation: not started
```

No Governance API endpoint, database, Hermes, Brain, Agent, secret, cryptography, or external connector is implemented. `src/iios_governance/` is a local, deterministic, in-memory reference implementation with 133 passing tests, 97% coverage, clean lint/type-check — it is not a production system, has no network listener, and cannot execute any external action (Governance decides, it never executes). No Brain or Agent is activated — every entry in `docs/BRAIN_REGISTRY.md` and `docs/AGENT_REGISTRY.md` remains `specified`/`not_implemented`.

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

Prove the ratified Governance Core specification (`docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`) is implementable, deterministic, and testable, via `GOV-IMP-001`: a local `iios_governance` Python package (`src/iios_governance/`) implementing the Invariant Kernel loader, Action Classifier, Policy Engine, Approval state machine, Capability contracts, append-only audit hash chain, and Kill Switch L1-L5, wired together in `GovernanceService.evaluate()`. No production cryptography, no external providers, no database — every store is in-memory or a read-only, checksum-verified filesystem load. `BACKLOG.md`'s next task after this merges is `HERMES-DEP-001` (design/preparation only; connecting to or modifying a real VPS needs a separate Owner decision).

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
