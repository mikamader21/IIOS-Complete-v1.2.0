# IIOS Master Implementation Program

**Version:** 0.1.0
**Status:** Specified, governs phase sequencing
**Parent authority:** `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, `AUTONOMY_PROTOCOL.md`

## Purpose

Organize IIOS's build-out by phase and dependency so that task selection (`BACKLOG.md`) always happens inside a known, ordered structure instead of ad hoc. No phase begins before its dependencies are `done`, and no phase's artifacts are presented as implemented before they carry running-system evidence.

## Phase status legend

`complete` — done, verified, evidence exists. `current` — in progress. Unlabeled/future phases have no status field yet because they have not started; they are not implicitly `blocked`, just not reached.

---

## Phase 0 — Foundation

- **Objective:** Establish IIOS's constitutional documents, Invariant Kernel, repository controls, and CI verification.
- **Dependencies:** None.
- **Artifacts:** `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, `governance/invariant-kernel/`, `.claude/settings.json`, `.github/workflows/verify-foundation.yml`, ADR-0001 through ADR-0009.
- **Acceptance criteria:** `docs/14_ACCEPTANCE_TESTS.md` Foundation criteria; `scripts/verify_foundation.py` and `scripts/verify_invariant_kernel.py` pass on Ubuntu and Windows.
- **Risks:** None outstanding — see `docs/18_AUDIT_DISPOSITION.md` for the Cowork-audit findings this phase resolved.
- **Authorization required:** Owner ratification (obtained — `docs/20_OWNER_RATIFICATION.md`).
- **Status:** complete
- **Definition of done:** Ratified `v1.2.1` tag, CI green on both platforms, Charter/Constitution/Kernel content stable.

## Phase 1 — Governance Core Specification

- **Objective:** Convert the Constitution and Invariant Kernel into implementable, testable technical contracts (Governance API, Action Classifier, Policy Engine, Approval Service, Capability model, Audit Event model, Kill Switch) before writing any backend.
- **Dependencies:** Phase 0.
- **Artifacts:** `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`, ADR-0010, ADR-0011, `governance/schemas/*.schema.json`.
- **Acceptance criteria:** All 20 mandatory decision cases resolved; structural schema validation passing; ADR-0010/ADR-0011 ratified.
- **Risks:** Concrete implementation library versions not yet pinned (`governance/schemas/README.md`); KMS/HSM/Vault product not yet selected (`docs/23_CAPABILITY_MODEL.md`).
- **Authorization required:** Owner ratification (obtained).
- **Status:** complete
- **Definition of done:** `v1.3.0` tag, "Governance Core specification: ratified / implementation: not started."

## Phase 2 — Autonomous Operating Layer

- **Objective:** Define the documentary and operational layer that lets Claude select, execute, validate, and deliver authorized work without per-file manual prompts, and that specifies (without activating) the Brain/Agent/Skill/Workflow architecture the rest of IIOS will be built on.
- **Dependencies:** Phase 1.
- **Artifacts:** `OWNER_PROFILE.md`, `AUTONOMY_PROTOCOL.md`, this file, `BACKLOG.md`, `docs/DOMAIN_CATALOG.md`, `docs/BRAIN_REGISTRY.md`, `docs/AGENT_REGISTRY.md`, `docs/SKILL_CATALOG.md`, `docs/WORKFLOW_REGISTRY.md`, `docs/TOOL_REGISTRY.md`, `docs/MODEL_ROUTING.md`, `docs/MEMORY_ARCHITECTURE.md`, `docs/SELF_EVOLUTION_PROTOCOL.md`, `docs/HANDOFF_PROTOCOL.md`, `docs/AUTONOMY_ACCEPTANCE_TESTS.md`, `work/`.
- **Acceptance criteria:** `docs/AUTONOMY_ACCEPTANCE_TESTS.md` passes conceptually; every Brain/Agent entry marked `specified`/`not_implemented`; no runtime, credential, or spend introduced.
- **Risks:** A large specification surface that must stay internally consistent as Phase 3+ begin to implement against it; mitigated by the same "specified, not implemented" discipline used in Phase 1.
- **Authorization required:** This instruction (Owner-authorized, two consecutive phases, no intermediate approval required within scope).
- **Status:** current
- **Definition of done:** PR merged, `BACKLOG.md` has at least one `ready` task for Phase 3.

## Phase 3 — Governance Core Implementation

- **Objective:** Build the actual Governance API, Policy Engine, Approval Service, capability issuer/verifier, and audit storage specified in Phase 1.
- **Dependencies:** Phase 2 (backlog and autonomy protocol must exist to sequence this work).
- **Artifacts:** Not yet created. Will include real service code, a policy bundle, a signing key management integration, and an audit store.
- **Acceptance criteria:** Not yet defined beyond Phase 1's specification; concrete tests to be derived from `docs/21_GOVERNANCE_CORE_SPEC.md`'s conceptual test matrix.
- **Risks:** First phase involving real credentials (signing keys) and a real database — highest-risk phase before Phase 6.
- **Authorization required:** Explicit Owner authorization to begin implementation (not granted by Phase 1/2 ratification alone).
- **Status:** not started
- **Definition of done:** Governance API passes its own acceptance tests in CI; Kernel/Charter/Constitution still unchanged.

## Phase 4 — Knowledge and Memory Infrastructure

- **Objective:** Stand up the Obsidian Vault, Graphify indexing, and the memory architecture defined in `docs/MEMORY_ARCHITECTURE.md`.
- **Dependencies:** Phase 2.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Not yet defined.
- **Risks:** Graphify must never become an authority source (`docs/MEMORY_ARCHITECTURE.md` — Rules).
- **Authorization required:** Explicit Owner authorization.
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 5 — Developer Brain and Build Runtime

- **Objective:** Activate the Developer Brain (`docs/BRAIN_REGISTRY.md`) as the first operating Brain, capable of building further IIOS components under Governance.
- **Dependencies:** Phase 3.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Not yet defined.
- **Risks:** First Brain to move from `specified` to active — sets the precedent for every later Brain activation.
- **Authorization required:** Explicit Owner authorization.
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 6 — Hermes Runtime Integration

- **Objective:** Integrate Hermes as the persistent execution runtime per `docs/HANDOFF_PROTOCOL.md`.
- **Dependencies:** Phase 3, Phase 5.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Not yet defined.
- **Risks:** First phase granting a runtime persistent, scheduled execution — sandboxing and credential-forwarding controls from `docs/03_GOVERNANCE_SECURITY.md` (Hermes baseline) apply in full.
- **Authorization required:** Explicit Owner authorization.
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 7 — Control Center MVP

- **Objective:** Build the Owner-facing command/evidence/approval/audit surface per `docs/11_CONTROL_CENTER_PRD.md`.
- **Dependencies:** Phase 3, Phase 4.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** `docs/11_CONTROL_CENTER_PRD.md` MVP modules.
- **Risks:** Not yet assessed.
- **Authorization required:** Explicit Owner authorization.
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 8 — Trading and Prop Firm Domain

- **Objective:** Activate Trading Brain and Prop Firm Brain in read-only observability mode (`docs/PROJECT_STATE.md` — Proposed first domain).
- **Dependencies:** Phase 3, Phase 5, Phase 7.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Read-only only; no order endpoints, per Constitution Article IV-D.
- **Risks:** Highest-scrutiny domain given Constitution's financial-write prohibition; every capability here is Class A/C only, never D.
- **Authorization required:** Explicit Owner authorization; first domain selection still an open Owner decision (`PROJECT_STATE.md`).
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 9 — Blockchain Intelligence Domain

- **Objective:** Activate Blockchain Brain for research/audit use cases.
- **Dependencies:** Phase 3, Phase 5.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Not yet defined.
- **Risks:** Not yet assessed.
- **Authorization required:** Explicit Owner authorization.
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 10 — Remaining Domain Brains

- **Objective:** Activate the remaining Brains in `docs/BRAIN_REGISTRY.md` (Research, Risk and Audit, Knowledge, Regulation, Finance, Gnosis, Health and Performance, Personal Operations) as each becomes relevant.
- **Dependencies:** Phase 3, Phase 5.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Not yet defined.
- **Risks:** Not yet assessed.
- **Authorization required:** Explicit Owner authorization, per Brain.
- **Status:** not started
- **Definition of done:** Not yet defined.

## Phase 11 — Self-Evolution and Optimization

- **Objective:** Activate the bounded self-improvement loop in `docs/SELF_EVOLUTION_PROTOCOL.md` (model evaluation, prompt optimization, skill-gap detection) without ever expanding IIOS's own authority.
- **Dependencies:** Phase 3 through Phase 10 substantially complete.
- **Artifacts:** Not yet created.
- **Acceptance criteria:** Not yet defined.
- **Risks:** Highest governance-discipline requirement — this is the phase most structurally similar to what the Constitution's "no agent approves its own privilege expansion" invariant exists to prevent from going wrong.
- **Authorization required:** Explicit Owner authorization.
- **Status:** not started
- **Definition of done:** Not yet defined.

---

No dates are stated anywhere in this document — sequencing is by dependency and Owner authorization, not by calendar.
