# IIOS Autonomous Backlog

**Status:** Specified, governs task selection under `AUTONOMY_PROTOCOL.md`
**Parent authority:** `MASTER_IMPLEMENTATION_PROGRAM.md`

## How to read this file

Each task is a fenced block with the fields below. `status` values: `proposed`, `ready`, `in_progress`, `blocked`, `review`, `done`, `superseded`. `priority` values: `P0` (blocking), `P1` (high), `P2` (normal), `P3` (low). `risk_class` is a Constitution Article IV action class (A/B/C/D) for the *documentation/specification work itself* — building a spec for a Class C or D capability is still Class B work (feature-branch documentation), unless stated otherwise. Per `AUTONOMY_PROTOCOL.md`, Claude selects the highest-priority `ready` task whose `dependencies` are all `done`, without asking the Owner what to do next.

---

```text
ID: AOL-001
title: Define IIOS Autonomous Operating Layer
phase: Phase 2 — Autonomous Operating Layer
status: review
priority: P0
dependencies: []
risk_class: B
owner_decision_required: none — authorized by the Owner's two-phase instruction (23 July 2026)
deliverables:
  - OWNER_PROFILE.md
  - AUTONOMY_PROTOCOL.md
  - MASTER_IMPLEMENTATION_PROGRAM.md
  - BACKLOG.md
  - docs/DOMAIN_CATALOG.md
  - docs/BRAIN_REGISTRY.md
  - docs/AGENT_REGISTRY.md
  - docs/SKILL_CATALOG.md
  - docs/WORKFLOW_REGISTRY.md
  - docs/TOOL_REGISTRY.md
  - docs/MODEL_ROUTING.md
  - docs/MEMORY_ARCHITECTURE.md
  - docs/SELF_EVOLUTION_PROTOCOL.md
  - docs/HANDOFF_PROTOCOL.md
  - docs/AUTONOMY_ACCEPTANCE_TESTS.md
  - work/NOW.md, work/NEXT.md, work/BLOCKED.md, work/DONE.md
acceptance_tests: docs/AUTONOMY_ACCEPTANCE_TESTS.md
```

```text
ID: GOV-IMP-001
title: Governance Core implementation skeleton
phase: Phase 3 — Governance Core Implementation
status: blocked
priority: P0
dependencies: [AOL-001]
risk_class: C
owner_decision_required: >
  Explicit Owner authorization to begin Governance Core implementation is required
  before this task may move from blocked/ready to in_progress — Phase 1's
  specification ratification is not itself that authorization (see
  MASTER_IMPLEMENTATION_PROGRAM.md — Phase 3, "Authorization required").
deliverables:
  - Not yet created. Expected to include a minimal Governance API skeleton
    (structure only), a first policy bundle conforming to the format specified
    in docs/22_POLICY_ENGINE_EVALUATION.md, and a test harness implementing the
    conceptual test matrix in docs/21_GOVERNANCE_CORE_SPEC.md.
acceptance_tests: >
  Not yet defined beyond docs/21_GOVERNANCE_CORE_SPEC.md's conceptual test
  matrix and the 20 mandatory decision cases; concrete tests to be authored
  as part of this task once authorized.
```

---

## Notes

- `GOV-IMP-001` becomes the next candidate for `ready` once `AOL-001` is `done` (this PR merged) — but per this phase's explicit instruction, it **must not begin on `feature/autonomous-operating-layer`**, and per the `owner_decision_required` field above, it additionally needs explicit Owner authorization to implement (not just to specify) before any session may move it past `blocked`.
- This backlog intentionally starts small. Additional Phase 2-adjacent documentation tasks (e.g. per-Brain detail specs, per-Skill test definitions) are expected to be filed as `proposed` by whichever session next reads `docs/BRAIN_REGISTRY.md`/`docs/SKILL_CATALOG.md` and finds a gap — that filing itself is autonomy-permitted (drafting derived documentation, `AUTONOMY_PROTOCOL.md`).
- No task in this file authorizes financial action, secret handling, or infrastructure deployment. Any such task must carry `owner_decision_required` naming the specific decision needed, per `AUTONOMY_PROTOCOL.md` — Stop conditions.
