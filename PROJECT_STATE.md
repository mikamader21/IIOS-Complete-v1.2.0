# IIOS Project State

**Version:** 1.3.0 — Governance Core Specification (tagged, `v1.3.0` → `aa9ec6d66f4c7c84ee8218d3b5901d888086c76f`); Governance Core implementation skeleton merged and CI-verified; Hermes VPS deployment package merged and topology-reconciled
**Review date:** 23 July 2026
**Phase:** 3 — Governance Core Implementation, first task done; Phase 6 (Hermes Runtime Integration) design/preparation complete and reconciled, real VPS install (`HERMES-INSTALL-001`) next (see `MASTER_IMPLEMENTATION_PROGRAM.md`)
**Status:** Foundation (Phase 0), Governance Core Specification (Phase 1), Autonomous Operating Layer (Phase 2), and the Governance Core implementation skeleton (Phase 3's `GOV-IMP-001`) are complete. Phase 2 merged (PR #6, commit `83c2c73`, merge commit `1f4ea9762cb5a2060cc38746af057c63ef2286a7`). `GOV-IMP-001` merged (PR #7, commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`), CI verified green — 4/4 checks, run `30047219545`. `HERMES-DEP-001` merged (PR #10, merge commit `fff907f84a5917489c02447965ee78b8ad0ea25c`), CI verified green — 5/5 checks, run `30051091906` — then reconciled against the real upstream `NousResearch/hermes-agent` product a second time before any VPS install: verified release pin (v0.19.0, tag `v2026.7.20`, commit `3ef6bbd201263d354fd83ec55b3c306ded2eb72a`, Docker digest `sha256:a6ce64e2038867885c2c90f6602425e6e70293d5e6d952a0e603a99265e01c40` linux/amd64) and a corrected topology (one container hosting multiple s6-supervised profiles, not one container per profile). ADR-0010 and ADR-0011 are **ratified**; ADR-0013 (Hermes VPS deployment model) is now **Ratified** (for controlled deployment preparation, not for financial execution or unrestricted agent activation); ADR-0012 (policy bundle format) remains **Proposed**. The Owner has authorized VPS purchase; `HERMES-INSTALL-001` (`BACKLOG.md`) is `blocked_by_owner_vps_details` pending non-secret VPS metadata and confirmed SSH access.

```text
Governance Core specification: ratified
Governance Core implementation skeleton: done
Governance Core production implementation: not started
Hermes VPS deployment package: done (merged and reconciled)
VPS installation: not authorized to execute yet — blocked_by_owner_vps_details
Hermes runtime: not installed
onyx profile: specified, not activated (first profile)
ict-trading profile: specified, not activated (future profile)
COO Brain: specified, not implemented
ONYX: specified, not implemented, not activated
```

`HERMES-DEP-001` was checked twice against the real `NousResearch/hermes-agent` product: a pre-merge audit (v0.19.0, removed a fabricated "worker" systemd unit and a redundant gateway-supervising unit, corrected an invalid `terminal.home_mode` value) and, after merge, a deeper reconciliation that re-verified the exact release/commit/Docker-digest pin and corrected the deployment topology to match the product's own current recommended pattern (one container, multiple profiles, not one container per profile). Full detail: `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`, `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`. No real VPS was touched at any point in either round.

Per a separate Owner directive, ONYX (Executive Orchestrator, `docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md`) is specified as the **first** planned Hermes profile — `ict-trading` is a future, not-yet-activated profile alongside further future profiles (`developer`, `research`, `knowledge`, `blockchain`, `regulation`) mapping onto already-specified Brains. ONYX operationalizes the pre-existing `BRAIN-COO` entry (`docs/BRAIN_REGISTRY.md`) as a new `AGENT-ONYX` (`docs/AGENT_REGISTRY.md`). ONYX v0.1 ("Executive Observer") is read-only by design — no write, no capability, no secret access, no financial action, no self-approval. It was not implemented, installed, or activated.

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

`GOV-IMP-001` is done: the ratified Governance Core specification (`docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`) is proven implementable, deterministic, and testable via the local `iios_governance` Python package (`src/iios_governance/`) — Invariant Kernel loader, Action Classifier, Policy Engine, Approval state machine, Capability contracts, append-only audit hash chain, and Kill Switch L1-L5, wired together in `GovernanceService.evaluate()`. No production cryptography, no external providers, no database — every store is in-memory or a read-only, checksum-verified filesystem load.

`HERMES-DEP-001` is done: the Hermes VPS deployment package — threat model, unprivileged service user, directory structure, egress allowlist, firewall, systemd units, backups, logs, health checks, rollback procedure, secret-injection design (no real secrets), `onyx` (first profile) and `ict-trading` (future profile) manifests, and install/uninstall runbooks — reconciled against the real upstream product and topology-corrected. Current objective is `HERMES-INSTALL-001`: installing the pinned Hermes image on the Owner-authorized, Owner-purchased real VPS once its remaining dependencies (non-secret VPS metadata, confirmed SSH access) are supplied. That install creates the `onyx` profile but does not activate it — activation is `ONYX-CORE-001`'s own further-gated scope, requiring the install completed, `hermes doctor` passed, the container healthy, a backup baseline, and a real Governance fail-closed test.

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
4. VPS purchase authorized by the Owner (23 July 2026) — specific provider and monthly ceiling still to be confirmed as part of `HERMES-INSTALL-001`'s dependency list (`BACKLOG.md`).
5. Set daily and monthly model-cost hard limits.
6. Confirm first domain.
7. Decide Vault sync method; backup remains separate.

## Prohibited assumptions

Research cost ranges are not budgets. Runtime self-evolution is not production-approved. Graphify is not authoritative. GPU is optional. Connector availability is not permission. No autonomous financial action is authorized.
