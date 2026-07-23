# IIOS Autonomous Backlog

**Status:** Specified, governs task selection under `AUTONOMY_PROTOCOL.md`
**Parent authority:** `MASTER_IMPLEMENTATION_PROGRAM.md`

## How to read this file

Each task is a fenced block with the fields below. `status` values: `proposed`, `ready`, `in_progress`, `blocked` (`blocked_by_dependency` is the specific case where the block is purely an unmet `dependencies` entry, as opposed to an `owner_decision_required` gate), `review`, `done`, `superseded`. `priority` values: `P0` (blocking), `P1` (high), `P2` (normal), `P3` (low). `risk_class` is a Constitution Article IV action class (A/B/C/D) for the *documentation/specification work itself* — building a spec for a Class C or D capability is still Class B work (feature-branch documentation), unless stated otherwise. Per `AUTONOMY_PROTOCOL.md`, Claude selects the highest-priority `ready` task whose `dependencies` are all `done`, without asking the Owner what to do next.

---

```text
ID: AOL-001
title: Define IIOS Autonomous Operating Layer
phase: Phase 2 — Autonomous Operating Layer
status: done
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
merged_as: PR #6, commit 83c2c73, merge commit 1f4ea9762cb5a2060cc38746af057c63ef2286a7
```

```text
ID: GOV-IMP-001
title: Governance Core implementation skeleton
phase: Phase 3 — Governance Core Implementation
status: done
priority: P0
dependencies: [AOL-001]
risk_class: C
owner_decision_required: resolved
authorization_source: Owner instruction, "AUTORIZACIÓN DEL OWNER — PHASE 3" (23 July 2026)
authorization_scope: implementation skeleton only — local, deterministic, in-memory
  adapters; no production cryptography, no external providers, no database, no
  execution of actions. Production implementation remains a separate, future
  authorization.
deliverables:
  - src/iios_governance/ (domain, application, ports, adapters/memory, adapters/filesystem)
  - governance/schemas/policy-bundle.schema.json + governance/policy-bundles/mvp/ (checksum-protected)
  - docs/ADR/ADR-0012-POLICY-BUNDLE-FORMAT.md (Proposed)
  - tests/governance/ — 133 tests, 97% coverage, covering the 20 mandatory decision
    cases plus duplicate request/idempotency, ambiguous classification, self-approval,
    expired/double-consumed approval, capability expiry/revocation/replay, policy
    version mismatch, budget exceeded, Governance/audit unavailable, Kernel/policy
    tampering, kill switch L1-L5, and deterministic replay of decision
  - docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md
  - CI: new governance-tests job (lint, format check, mypy, pytest+coverage) on
    ubuntu-latest + windows-latest, existing verify job untouched
  - pyproject.toml with pinned dependencies (jsonschema==4.26.0, pytest==9.1.1,
    pytest-cov==7.1.0, ruff==0.15.22, mypy==2.3.0, types-jsonschema==4.26.0.20260518)
acceptance_tests: >
  docs/21_GOVERNANCE_CORE_SPEC.md conceptual test matrix and 20 mandatory decision
  cases; docs/AUTONOMY_ACCEPTANCE_TESTS.md; concrete pytest suite under
  tests/governance/ (this task's own deliverable) — all passing, 97% coverage,
  clean ruff/mypy.
merged_as: PR #7, commit 381f525, merge commit bb4579bf82c6cddf65a5280e74b9327714340a45.
  CI verified green (4/4 checks: verify ubuntu/windows, governance-tests
  ubuntu/windows, run 30047219545).
```

```text
ID: HERMES-DEP-001
title: Secure Hermes VPS deployment package
phase: Phase 6 — Hermes Runtime Integration
status: done
priority: P0
dependencies: [GOV-IMP-001 merged and verified]  # satisfied: PR #7, merge commit bb4579b
risk_class: C
owner_decision_required: >
  false to design and prepare the package (documentation, scripts, configuration
  templates); true, separately, to actually connect to or modify any real VPS.
deliverables:
  - VPS threat model
  - unprivileged service user
  - directory structure
  - filesystem isolation
  - explicit terminal.cwd
  - terminal.home_mode
  - egress allowlist
  - firewall configuration
  - systemd unit(s)
  - backups
  - logs
  - health checks
  - update/rollback procedure
  - profile separation
  - secret injection design (no real secrets)
  - ict-trading profile package
  - installation runbook
  - uninstall/rollback runbook
deliverables_done:
  - docs/31_HERMES_DEPLOYMENT_PACKAGE.md
  - docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md (Proposed, amended post-audit)
  - deploy/hermes/ (README, directory-layout, scripts, systemd units, firewall,
    core/ compose template, secrets templates, ict-trading manifest + config.yaml
    template, five runbooks)
  - .github/workflows/verify-foundation.yml — hermes-deployment-tests CI job
audit: >
  Owner-directed pre-merge audit ("AUDITORIA PRE-MERGE — HERMES-DEP-001") checked
  this package against the real NousResearch/hermes-agent product (v0.19.0,
  2026-07-20, consulted 2026-07-23). Found and corrected: a fabricated "worker"
  systemd unit with no upstream basis, a gateway-supervising systemd unit
  duplicating Docker's own restart:unless-stopped, an invented
  terminal.home_mode value, an ict-trading manifest presented ambiguously
  against Hermes' real config.yaml format, a raw-tar backup duplicating the
  official `hermes backup` command, and an unsafe default-apply firewall
  script. Full list: docs/31_HERMES_DEPLOYMENT_PACKAGE.md — "Corrections after
  upstream audit". No real VPS was touched during the audit or its fixes.
reconciliation: >
  A second Owner-directed reconciliation ("FINAL UPSTREAM RECONCILIATION —
  BEFORE HERMES VPS INSTALLATION", 23 July 2026) re-verified the Hermes release
  pin (confirmed v0.19.0 / tag v2026.7.20 / commit 3ef6bbd201263d354fd83ec55b3c306ded2eb72a
  / Docker digest sha256:a6ce64e2038867885c2c90f6602425e6e70293d5e6d952a0e603a99265e01c40,
  linux/amd64 — the Owner's own "v0.18.2 latest" observation was a stale/
  pre-propagation read, resolved with evidence in ADR-0013) and corrected the
  deployment topology from one-container-per-profile to one container hosting
  multiple s6-supervised profiles, matching the product's own current
  recommended pattern. Full detail: docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md
  (now Ratified), docs/31_HERMES_DEPLOYMENT_PACKAGE.md.
status_detail: >
  HERMES-DEP-001: done (merged and reconciled)
  VPS installation: not authorized
  Hermes runtime: not installed
  onyx profile: specified, not activated (first profile)
  ict-trading profile: specified, not activated (future profile)
acceptance_tests: docs/14_ACCEPTANCE_TESTS.md — "Hermes VPS deployment package (HERMES-DEP-001)"
note: Design/preparation scope only across both this task and its reconciliation —
  no real VPS was provisioned, connected to, or modified, and no script under
  deploy/hermes/ was executed against a real host. Connecting to or modifying a
  real VPS is HERMES-INSTALL-001's own separate authorization.
merged_as: PR #10, merge commit fff907f84a5917489c02447965ee78b8ad0ea25c. CI
  verified green (5/5 checks: verify ubuntu/windows, governance-tests
  ubuntu/windows, hermes-deployment-tests, run 30051091906).
```

```text
ID: HERMES-INSTALL-001
title: Install pinned Hermes base on authorized VPS
phase: Phase 6 — Hermes Runtime Integration
status: blocked_by_owner_vps_details
priority: P0
dependencies:
  - reconciled deployment package merged (HERMES-DEP-001, done)
  - CI green
  - ADR-0013 ratified (done — docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md)
  - VPS purchased (Owner-authorized 23 July 2026)
  - Ubuntu provisioned
  - Owner supplies non-secret VPS metadata (IP/hostname, architecture, provider)
  - Owner confirms SSH public-key access
risk_class: C
owner_decision_required: true — this task connects to and installs software on a
  real VPS, a standing AUTONOMY_PROTOCOL.md stop condition. The Owner has
  authorized VPS purchase and preparation for this installation, but the
  installation itself does not proceed until every dependency above is met and
  a final go-ahead is given.
deliverables:
  - Pinned Hermes container running per deploy/hermes/core/docker-compose.yml.template
  - Firewall applied (deploy/hermes/firewall/apply-ufw-rules.sh --apply)
  - Backup and health-check systemd timers enabled and verified
  - onyx profile created (not activated) per deploy/hermes/runbooks/INSTALL.md
  - Install recorded in work/DONE.md / CHANGELOG.md with pinned digest, date, host identifier
acceptance_tests: deploy/hermes/runbooks/INSTALL.md steps 1-14, all verified against
  the real host, not simulated.
note: This is the first task in this backlog authorized to touch a real VPS. It
  installs and health-checks Hermes and creates the onyx profile — it does NOT
  activate onyx (no credential, no gateway start) and does NOT activate
  ict-trading. Activation is ONYX-CORE-001's own separate, further-gated scope.
```

```text
ID: ONYX-CORE-001
title: ONYX Executive Observer profile
phase: Phase 6 — Hermes Runtime Integration
status: blocked_by_dependency
priority: P0
dependencies:
  - HERMES-DEP-001 merged and verified (done)
  - ADR-0013 ratified (done — docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md)
  - HERMES-INSTALL-001 completed
  - hermes doctor passed (real, on the installed host)
  - container healthy (docker compose ps / healthcheck green, sustained)
  - backup baseline completed (at least one verified, restore-tested backup exists)
  - Governance fail-closed test passed (a real, executed test — not the
    conceptual acceptance criteria in docs/14_ACCEPTANCE_TESTS.md — confirming
    Governance-unavailable behavior denies rather than silently allows, once
    Governance Core has an execution surface to test against)
  - VPS connection explicitly authorized by Owner (satisfied for
    HERMES-INSTALL-001's preparation scope; activation itself remains
    separately gated by owner_decision_required below)
risk_class: C
owner_decision_required: true — activation on a real VPS requires explicit Owner
  authorization, independent of and in addition to the dependencies above.
authorization_source: Owner instruction, "OWNER DIRECTIVE — ADD ONYX REFERENCE BEFORE
  HERMES-DEP-001 PR" (23 July 2026) — specification/manifest/backlog only, this task
  itself does not implement, install, or activate ONYX.
deliverables_done:
  - docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md
  - deploy/hermes/profiles/onyx/onyx.profile.json (specified, not_activated, read_only,
    all financial/main_merge/release_creation/vps_modification/self_approval flags false)
  - docs/AGENT_REGISTRY.md — AGENT-ONYX (parent_brain BRAIN-COO)
future_deliverables:
  - native Hermes profile (config.yaml — no materializer exists yet, docs/32 section 7)
  - SOUL.md, USER.md, minimal curated MEMORY.md, AGENTS.md
  - allowed-tools list
  - Governance client
  - audit client
  - executive briefing format implementation (docs/32 — "Executive report format")
  - health check
  - restart test
  - fail-closed tests
acceptance_tests: docs/14_ACCEPTANCE_TESTS.md — "ONYX Executive Orchestrator (ONYX-CORE-001,
  specification only)"
note: Specification-only task. No profile was activated, no VPS was touched, no software
  was installed. The manifest's path convention was corrected in the topology
  reconciliation (docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md Amendment 2) —
  onyx is now specified as a named profile inside the single shared Hermes
  container, not a dedicated /srv/iios/ container as an earlier draft had it.
```

```text
ID: ONYX-GOV-001
title: Connect ONYX to Governance and Audit
phase: Phase 6 — Hermes Runtime Integration
status: blocked_by_dependency
priority: P1
dependencies: [ONYX-CORE-001]
risk_class: C
owner_decision_required: true — any real Governance/Audit connection is a standing
  AUTONOMY_PROTOCOL.md stop condition independent of this entry.
deliverables: Not yet defined — scoping depends on ONYX-CORE-001 and on Governance Core's
  production implementation (docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md — the current
  skeleton has no execution surface to connect to).
acceptance_tests: Not yet defined.
```

```text
ID: ONYX-BUILD-001
title: Developer Brain delegation bridge
phase: Phase 6 — Hermes Runtime Integration
status: blocked_by_dependency
priority: P1
dependencies:
  - ONYX-GOV-001
  - Developer Brain implementation (BRAIN-DEVELOPER, MASTER_IMPLEMENTATION_PROGRAM.md Phase 5)
  - tool authorization
  - GitHub integration
risk_class: C
owner_decision_required: true — delegating build authority through ONYX to Developer Brain
  is a new capability requiring explicit Owner authorization.
deliverables: Not yet defined.
acceptance_tests: Not yet defined.
```

```text
ID: ICT-KNOW-001
title: ICT source inventory and canonical knowledge pack
phase: Phase 4 — Knowledge and Memory Infrastructure
status: blocked_by_dependency
priority: P1
dependencies: [ONYX-BUILD-001, Owner-confirmed location of source projects/documents]
risk_class: B
owner_decision_required: >
  true — the location of the Owner's existing ICT source projects/documents must be
  confirmed before this task can be scoped, let alone started.
sequence_note: Reordered per the Owner's explicit sequence (23 July 2026): Hermes base
  installed -> ONYX-CORE-001 -> ONYX-GOV-001 -> ONYX-BUILD-001 -> ICT-KNOW-001 ->
  ICT-AGENT-001. GOV-IMP-001 (this task's original dependency) is done; ONYX-BUILD-001
  is the new gating dependency per that sequence, in addition to the unchanged
  Owner-location decision below.
deliverables: Not yet defined — scoping itself depends on the Owner decision above.
acceptance_tests: Not yet defined.
```

```text
ID: ICT-AGENT-001
title: Hermes ICT Trading read-only profile
phase: Phase 8 — Trading and Prop Firm Domain
status: blocked_by_dependency
priority: P1
dependencies: [HERMES-DEP-001, ICT-KNOW-001, authorized Hermes installation, approved Governance tests]
risk_class: C
owner_decision_required: true — Hermes installation itself is a standing stop condition
  (AUTONOMY_PROTOCOL.md) requiring explicit authorization, independent of this task.
deliverables: Not yet defined.
acceptance_tests: Not yet defined. Read-only only — no order endpoints, per Constitution
  Article IV-D.
```

```text
ID: CONTROL-UI-001
title: IIOS Mission Control MVP
phase: Phase 7 — Control Center MVP
status: blocked_by_dependency
priority: P1
dependencies: [Governance contracts, Hermes contracts, approved Stitch designs]
risk_class: B
owner_decision_required: true — design approval and Phase 7 authorization are Owner
  decisions not yet made.
deliverables: Not yet defined. Must include a minimal chat surface with ONYX
  (docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md) per the Owner's instruction, which
  referred to this requirement as "CONTROL-UI-BOOT-001" — no such ID exists in this
  backlog; recorded as a requirement on the existing CONTROL-UI-001 entry instead of
  inventing a new, possibly-duplicate ID. Flag this naming discrepancy to the Owner for
  confirmation before CONTROL-UI-001 is scoped.
acceptance_tests: docs/11_CONTROL_CENTER_PRD.md MVP modules, once scoped.
```

---

## Notes

- `AOL-001` is `done` (PR #6 merged, commit `83c2c73`, merge commit `1f4ea9762cb5a2060cc38746af057c63ef2286a7`).
- `GOV-IMP-001` is `done` (PR #7 merged, commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`; CI verified green, 4/4 checks, run `30047219545`).
- `HERMES-DEP-001` is `done` (PR #10 merged, merge commit `fff907f84a5917489c02447965ee78b8ad0ea25c`; CI verified green, 5/5 checks, run `30051091906`), then reconciled against the real upstream product a second time before any VPS install — see its `reconciliation` field and `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` (now **Ratified**).
- `HERMES-INSTALL-001` is the next real-VPS task, `blocked_by_owner_vps_details` — the Owner has authorized VPS purchase and preparation, but installation itself waits on the Owner supplying non-secret VPS metadata and confirming SSH access.
- `ONYX-CORE-001`, `ONYX-GOV-001`, `ONYX-BUILD-001` were added per the Owner's explicit sequencing instruction (23 July 2026): Hermes base installed -> ONYX-CORE-001 -> ONYX-GOV-001 -> ONYX-BUILD-001 -> ICT-KNOW-001 -> ICT-AGENT-001. `ONYX-CORE-001`'s dependencies were tightened in the reconciliation to require `HERMES-INSTALL-001` completed, `hermes doctor` passed, container healthy, a backup baseline, and a real (not conceptual) Governance fail-closed test — none of the three ONYX tasks is implemented, installed, or activated.
- `ICT-KNOW-001` was reordered after `ONYX-BUILD-001` per that sequence and still cannot be scoped until the Owner confirms where the source ICT projects/documents live.
- `ICT-AGENT-001` and `CONTROL-UI-001` depend on multiple upstream tasks not yet done; both remain `blocked_by_dependency`. `CONTROL-UI-001` additionally now requires a minimal ONYX chat surface — see that entry's `deliverables` for a flagged naming discrepancy in the Owner's instruction ("CONTROL-UI-BOOT-001") needing confirmation.
- This backlog intentionally starts small. Additional documentation-adjacent tasks are expected to be filed as `proposed` by whichever session finds a gap — that filing itself is autonomy-permitted (`AUTONOMY_PROTOCOL.md`).
- No task in this file authorizes financial action, secret handling, or unattended infrastructure deployment. Any such task must carry `owner_decision_required` naming the specific decision needed, per `AUTONOMY_PROTOCOL.md` — Stop conditions.
