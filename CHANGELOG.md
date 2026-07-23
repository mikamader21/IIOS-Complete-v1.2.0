# Changelog

## Unreleased — Hermes topology reconciliation and release-pin verification (pre-HERMES-INSTALL-001)

Owner-directed reconciliation ("FINAL UPSTREAM RECONCILIATION — BEFORE HERMES VPS INSTALLATION", 23 July 2026), performed on `main` after `HERMES-DEP-001` merged (PR #10, `fff907f`), before any real VPS action. The Owner authorized VPS purchase and preparation for installation as part of this instruction — this change does not itself connect to or install anything on a real VPS.

- **Re-verified the upstream release pin** against three independent official sources (GitHub releases page marked Latest, GitHub tags page, GitHub commit API with GPG signature verification) plus Docker Hub's own tag listing: Hermes Agent v0.19.0, tag `v2026.7.20`, commit `3ef6bbd201263d354fd83ec55b3c306ded2eb72a` (Teknium, Nous Research), Docker image `nousresearch/hermes-agent@sha256:a6ce64e2038867885c2c90f6602425e6e70293d5e6d952a0e603a99265e01c40` (linux/amd64; arm64 digest also recorded). Confirmed the Owner's own "v0.18.2 appears latest" observation was a stale/pre-propagation read — the release commit's own diff bumps the product's internal version string from 0.18.2 to 0.19.0, proving 0.18.2 was the immediately prior release, not a currently-latest one.
- **Corrected the deployment topology** from one container per profile to **one official Hermes container hosting multiple s6-supervised profiles**, matching the official documentation's own current recommendation ("the recommended deployment is one container hosting all profiles") — the one-container-per-profile pattern this repo had adopted was the product's pre-s6-migration pattern, superseded upstream.
- Updated `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` with the verified pin, the corrected topology, a "Real isolation boundaries" table stating plainly that co-located-profile separation is application-layer only (not OS/container-layer), and a "Future dedicated-container option" section for high-risk profiles — then changed its status to **Ratified** ("Ratified by Owner for controlled VPS deployment preparation. This ratification does not authorize financial execution or unrestricted agent activation.").
- Rewrote `deploy/hermes/core/docker-compose.yml.template` (pinned by digest, single service, no published ports by default, native `healthcheck:` block, `shm_size`) and added `deploy/hermes/core/compose.env.example`'s companion note explaining the three-file secret model doesn't change, only the shared-volume path.
- Updated `deploy/hermes/profiles/onyx/onyx.profile.json` and `ict-trading.profile.json`/`.config.yaml.template` for the shared-volume path convention (`/opt/data/profiles/<name>/`), flagging the exact `HERMES_HOME` resolution for named profiles as not independently confirmed pending a real `hermes profile create` run.
- Rewrote `run-backup.sh` to a plain host-level tar of the single shared `/opt/hermes/data` volume (removing the `docker` group requirement for backups entirely — the earlier per-profile-container design needed `docker exec`, this one doesn't) and `run-healthcheck.sh` to loop `hermes profile list` / `hermes -p <name> gateway status` over whatever profiles actually exist.
- Rewrote all five runbooks (`INSTALL.md`, `UNINSTALL_ROLLBACK.md`, `UPDATE_ROLLBACK.md`, `BACKUP_RESTORE.md`, `HEALTH_CHECKS.md`) for the corrected topology, including the official docs' explicit warning against two Hermes containers sharing one data directory, and an honest note that backup archives now contain live secrets once any profile is activated (a change from the earlier per-profile design's claim).
- Added `docs/14_ACCEPTANCE_TESTS.md` criteria for the reconciled topology and digest pin.
- Extended `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` and `deploy/hermes/README.md` with the reconciliation history and the isolation-model summary.
- `BACKLOG.md`: `HERMES-DEP-001` marked `done` (PR #10, merge commit `fff907f84a5917489c02447965ee78b8ad0ea25c`); added `HERMES-INSTALL-001` (`blocked_by_owner_vps_details`); tightened `ONYX-CORE-001`'s dependencies to require `HERMES-INSTALL-001` completed, `hermes doctor` passed, container healthy, a backup baseline, and a real (not conceptual) Governance fail-closed test.
- **No real VPS was provisioned, connected to, or modified. No script under `deploy/hermes/` was executed against a real host. No profile was activated. No credential was created.**
- Status:
  ```text
  Hermes VPS deployment package: done (merged and reconciled)
  ADR-0013: Ratified (deployment preparation only)
  VPS installation: blocked_by_owner_vps_details
  onyx profile: specified, not activated
  ```

## Unreleased — ONYX Executive Orchestrator specification (ONYX-CORE-001)

- Added `docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md`: ONYX as the persistent-agent operationalization of the pre-existing `BRAIN-COO` (`docs/BRAIN_REGISTRY.md`), specifying its mission, ONYX v0.1 ("Executive Observer") read-only authority list, permanent prohibitions (never modifies Charter/Constitution/Kernel, never self-approves, fails closed if Governance is unavailable), model-routing-only model access (no hardcoded provider/model), a future materialization pipeline (not implemented), a future workspace design under `/srv/iios/profiles/onyx/` (not created on any real system — flagged as inconsistent with `deploy/hermes/`'s established `/opt/hermes/profiles/<name>/` convention), and a future executive-briefing report format that separates verified facts, ONYX's own analysis, other agents' attributed proposals, and the Owner's reserved decision.
- Added `deploy/hermes/profiles/onyx/onyx.profile.json`: an IIOS deployment manifest (not native Hermes config, same pattern as `ict-trading.profile.json`) — `status: specified`, `activation_state: not_activated`, `execution_mode: read_only`, empty `capabilities`/`tools`/`secrets`, and every action gate (`financial_execution`, `self_approval`, `main_merge`, `release_creation`, `vps_modification`) `false`.
- Added `AGENT-ONYX` to `docs/AGENT_REGISTRY.md` (`parent_brain: BRAIN-COO`), explicitly distinguished from the pre-existing `AGENT-ORCHESTRATOR` (subordinate directly to Governance for already-approved-objective decomposition — ONYX sits one level up as the Owner-facing entry point).
- Noted ONYX in `docs/TOOL_REGISTRY.md`'s Hermes entry (`planned_first_profiles`, alongside `ict-trading`) and in `docs/HANDOFF_PROTOCOL.md` (anticipated originator role, not implemented — ONYX v0.1 has no write capability of any kind) and `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` (new section 19).
- Added `docs/14_ACCEPTANCE_TESTS.md` — "ONYX Executive Orchestrator (ONYX-CORE-001, specification only)".
- Added `BACKLOG.md` entries `ONYX-CORE-001`, `ONYX-GOV-001`, `ONYX-BUILD-001` (all `blocked_by_dependency`), per the Owner's explicit sequence: Hermes base installed -> `ONYX-CORE-001` -> `ONYX-GOV-001` -> `ONYX-BUILD-001` -> `ICT-KNOW-001` -> `ICT-AGENT-001`. Reordered `ICT-KNOW-001` after `ONYX-BUILD-001` in that dependency chain (its Owner-confirmed-source-location gate is unchanged and independent). Added a minimal-ONYX-chat requirement to `CONTROL-UI-001`, flagging that the Owner's instruction referred to it as "CONTROL-UI-BOOT-001" — no such ID exists in this backlog; recorded on the existing entry rather than inventing a possibly-duplicate one.
- Extended `scripts/verify_foundation.py` to require `docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md` and `deploy/hermes/profiles/onyx/onyx.profile.json`, and to assert the manifest's read-only/not-activated field values structurally, not just presence.
- Status:
  ```text
  COO Brain: specified, not implemented (pre-existing)
  ONYX: specified, not implemented, not activated
  Hermes: deployment package in review, runtime not installed
  ```
- **ONYX was not implemented, installed, or activated. No profile was started. No real VPS was touched.**

## Unreleased — Hermes VPS deployment package (HERMES-DEP-001)

- Added `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` (**Proposed**): dedicated unprivileged `hermes` service user, Docker Compose + systemd supervision, no public listener, default-deny egress allowlist, explicit `terminal.cwd`/`terminal.home_mode`, two-layer filesystem isolation (application + host), out-of-band secret injection, encrypted scheduled backups, pinned-version update/rollback, read-only `ict-trading` first profile.
- Added `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`: the design write-up covering all eighteen `HERMES-DEP-001` deliverables, a VPS threat model, and an explicit "what this task did not do" section.
- Added `deploy/hermes/`: `README.md`, `directory-layout.md`; `scripts/` (`create-service-user.sh`, `bootstrap-directories.sh`, `run-backup.sh`, `run-healthcheck.sh`); `systemd/` (`hermes-gateway.service`, `hermes-worker.service`, `hermes-backup.service`+`.timer`, `hermes-healthcheck.service`+`.timer`); `firewall/` (`apply-ufw-rules.sh`, `egress-allowlist.md`); `secrets/` (`env.template` with placeholder values only, `README.md` describing the injection design); `profiles/ict-trading.profile.json` (read-only, no order endpoint, no standing Governance capability); `runbooks/` (`INSTALL.md`, `UNINSTALL_ROLLBACK.md`, `UPDATE_ROLLBACK.md`, `BACKUP_RESTORE.md`, `HEALTH_CHECKS.md`).
- Extended `scripts/verify_foundation.py` to require presence of every file above and structurally validate `deploy/hermes/profiles/ict-trading.profile.json` as JSON.
- Added a "Hermes VPS deployment package (HERMES-DEP-001)" section to `docs/14_ACCEPTANCE_TESTS.md`.
- Noted the design package's existence in `docs/TOOL_REGISTRY.md`'s Hermes entry (`deployment_package` field) without changing its `status: not integrated`.
- **No real VPS was provisioned, connected to, or modified. No script under `deploy/hermes/` was executed. No real secret, API key, or credential was created, requested, or stored.** Hermes remains not integrated; the `ict-trading` profile has no live connection to any account or data provider.

**Pre-merge audit corrections (same task, before merge):** the Owner required auditing this package against the real `NousResearch/hermes-agent` product (v0.19.0, 2026-07-20, consulted 2026-07-23) instead of relying on this repository's own general infrastructure docs. Corrections: removed the fabricated `hermes-worker.service` (no such process/subcommand exists upstream) and the `hermes-gateway.service` wrapping `docker compose up/down` (duplicated Docker's own `restart: unless-stopped` supervision); added a real, pinned `deploy/hermes/core/docker-compose.yml.template` and `compose.env.example`; corrected `terminal.home_mode` from the invented `profile_scoped` to the real value `profile`; reversed `terminal.backend` for `ict-trading` from `docker` to `local` to avoid a `docker.sock` mount; reframed `ict-trading.profile.json` as an explicit IIOS deployment manifest and added `ict-trading.config.yaml.template` as its real-format counterpart; rewrote `run-backup.sh` to call the official `hermes backup` command instead of a raw `tar`; rewrote `run-healthcheck.sh` to use `hermes doctor`/`hermes gateway status` plus host disk/memory/restart-loop checks; rewrote `apply-ufw-rules.sh` to be dry-run by default, requiring `--apply`/`--apply-egress`, with a pre-flight SSH-source check and an `at`-based rollback safety net, and removed an `eval`-based dispatch in favor of real argument arrays; set the executable bit on every `.sh` file (previously `100644`); added `*.example` to `.gitattributes`' LF rules; added a `hermes-deployment-tests` CI job (`bash -n`, ShellCheck, `systemd-analyze verify` against a `hermes` user/stub scripts staged only on the disposable CI runner, line-ending and credential-shape checks, and a structural check that the `ict-trading` manifest forbids financial execution). Full list: `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` — "Corrections after upstream audit"; ADR amendment: `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`. ADR-0013 remains **Proposed**. No real VPS was touched during the audit or its fixes.
- Status:
  ```text
  Hermes VPS deployment package: in review
  VPS installation: not authorized
  Hermes runtime: not installed
  ict-trading profile: specified, not activated
  ```

## Unreleased — Governance Core implementation skeleton (GOV-IMP-001) — merged

Merged as PR #7 (commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`), CI verified green post-merge: 4/4 checks (`verify` ubuntu-latest/windows-latest, `governance-tests` ubuntu-latest/windows-latest), run `30047219545`. Branch `feature/governance-core-skeleton` deleted (local and remote) after verification.

- Added `src/iios_governance/`: a local, deterministic, in-memory reference implementation of the ratified Governance Core specification — `domain/` (models, action_classifier, policy_engine, approval_service, capability_service, audit_chain, kill_switch, reason_codes, errors), `application/` (decision_pipeline, governance_service), `ports/` (9 Protocols), `adapters/memory/` and `adapters/filesystem/`. Governance decides; it never executes an external action — no HTTP transport, no database, no network call exists in this package.
- Added `governance/schemas/policy-bundle.schema.json` and the MVP bundle `governance/policy-bundles/mvp/` (checksum-protected, same canonical-hash pattern as the Invariant Kernel). Format recorded in `docs/ADR/ADR-0012-POLICY-BUNDLE-FORMAT.md` (**Proposed**, not yet Ratified).
- Added `tests/governance/`: 133 tests, 97% coverage, covering the 20 mandatory decision cases plus duplicate request/idempotency, ambiguous classification, self-approval rejection, expired/double-consumed approval, capability expiry/revocation/replay/algorithm-downgrade rejection (`EdDSA` explicitly denied), policy version mismatch, budget exceeded, Governance/audit unavailable, Kernel/policy-bundle tampering detection, Kill Switch L1-L5, and deterministic replay of decision. No test calls a network endpoint or depends on real wall-clock time.
- No production cryptography: `DisabledSignatureVerifier` (fails closed with `CAPABILITY_CRYPTO_NOT_IMPLEMENTED`) is the only signature verifier wired into production code. No Ed25519 library, no RFC 8785 JCS library, no KMS/HSM/Vault integration.
- Added `pyproject.toml` with pinned dependencies: `jsonschema==4.26.0` (`Draft202012Validator`), `pytest==9.1.1`, `pytest-cov==7.1.0`, `ruff==0.15.22`, `mypy==2.3.0`, `types-jsonschema==4.26.0.20260518` — all resolved from the live index during this task, not guessed.
- Extended `.github/workflows/verify-foundation.yml` with a new `governance-tests` job (lint, format check, type check, pytest+coverage) on `ubuntu-latest` and `windows-latest`; the existing `verify` job is unchanged.
- Added `docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md`: structure, evaluation flow, functional/simulated/not-implemented component breakdown, security boundaries, local test instructions.
- Extended `.gitignore` for Python build/tooling artifacts (`*.egg-info/`, `.mypy_cache/`, `.ruff_cache/`, `.coverage`, `htmlcov/`, `build/`) and `scripts/verify_foundation.py`'s secret scan to skip them.
- Status:
  ```text
  Governance Core implementation skeleton: done
  Governance Core production implementation: not started
  ```

## Unreleased — IIOS Autonomous Operating Layer — merged

- Added `OWNER_PROFILE.md`: stable professional/operational context for the Owner. No family, medical, or intimate data.
- Added `AUTONOMY_PROTOCOL.md`: the normal build cycle, the explicit list of actions Claude does not need to ask authorization for, and the hard stop conditions (Charter/Constitution/Kernel change, financial permissions, secrets, spend, production deploy, destructive migration, financial operation, irreversible action, merge to `main`, release tag, ratified-document contradiction, Owner-only business decision, uncovered high risk, real technical blocker).
- Added `MASTER_IMPLEMENTATION_PROGRAM.md`: 12 phases (0–11) from Foundation through Self-Evolution, each with objective, dependencies, artifacts, acceptance criteria, risks, authorization requirement, status, and definition of done. No dates.
- Added `BACKLOG.md`: task-tracking format (`ID/title/phase/status/priority/dependencies/risk_class/owner_decision_required/deliverables/acceptance_tests`), seeded with `AOL-001` (this phase, `review`) and `GOV-IMP-001` (Governance Core implementation skeleton, `blocked` on `AOL-001`, additionally requiring separate Owner authorization to begin implementation).
- Added `docs/DOMAIN_CATALOG.md`, `docs/BRAIN_REGISTRY.md` (14 Brains), `docs/AGENT_REGISTRY.md` (7 persistent roles + 9 ephemeral agent types), `docs/SKILL_CATALOG.md` (19 categories), `docs/WORKFLOW_REGISTRY.md` (16 workflows), `docs/TOOL_REGISTRY.md` (17 tool categories; Hermes, Graphify, Supabase, MetaApi, and Make.com explicitly marked not integrated), `docs/MODEL_ROUTING.md` (functional roles, complementing the existing tier-based `docs/06_MODEL_ROUTING.md`), `docs/MEMORY_ARCHITECTURE.md`, `docs/SELF_EVOLUTION_PROTOCOL.md`, `docs/HANDOFF_PROTOCOL.md` (Claude ↔ Hermes), `docs/AUTONOMY_ACCEPTANCE_TESTS.md`.
- Added `work/NOW.md`, `work/NEXT.md`, `work/BLOCKED.md`, `work/DONE.md`, `work/README.md`.
- Every Brain and Agent entry is `specified`/`not_implemented`; every Skill entry is `cataloged`. None is activated.
- Updated `AGENTS.md` and `CLAUDE.md`: session-start reading order (`PROJECT_STATE.md` → `AUTONOMY_PROTOCOL.md` → `work/NOW.md` → `BACKLOG.md`), "do not ask what to do next while an authorized `ready` task exists," "do not interpret documentation status as implementation status," and a pointer to `OWNER_PROFILE.md` instead of an inline biography.
- Extended `scripts/verify_foundation.py` to require presence of all Phase 2 artifacts.
- No backend, database, migration, MCP, model call, service, connector, infrastructure, credential, or financial capability was implemented. No change to `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, or `governance/invariant-kernel/invariants.json`.
- Merged as PR #6 (commit `83c2c73`, merge commit `1f4ea9762cb5a2060cc38746af057c63ef2286a7`), CI verified green post-merge. Branch `feature/autonomous-operating-layer` deleted (local and remote) after verification.

## 1.3.0 — Governance Core Specification — 23 July 2026

Tagged `v1.3.0` → `aa9ec6d66f4c7c84ee8218d3b5901d888086c76f`, after merge (PR #5) and green CI (Ubuntu + Windows) post-merge verification.

- Added `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`: technical specification of the Governance API, Action Classifier, Orchestrator Boundary, Policy Engine, Capability Model (claims / protected header / wire token contracts), Approval Model, Audit Event Model (RFC 8785 recommended for canonicalization), and Kill Switch.
- Added `docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md` recording the boundary decisions and discarded alternatives. **Ratified by the Owner, 23 July 2026.**
- Added `docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md`, **ratified by the Owner, 23 July 2026**, fixing concrete MVP parameters: idempotency window (24h, configurable to 7 days), actor authentication (OIDC+MFA+WebAuthn for humans, mTLS+workload identity for services/agents/runtimes), Class C approval TTL (15 min default, 60 min max non-production), single-approver MVP, capability envelope format and key custody (KMS/HSM/Vault, 90-day rotation), capability TTLs by class, rate limiting independent of Cost Governance, `audience` single-valued for MVP, Make.com classification (read-only metadata Class A via allowlisted connector, all mutations Class C), kill-switch drill cadence, and the JSON Schema validation library (Python `jsonschema`, `Draft202012Validator`).
- **Corrected, same day (23 July 2026):** the capability envelope's cryptographic profile was tightened per Owner decision to **JWS Compact Serialization** (RFC 7515), `alg: "Ed25519"` (the fully-specified JOSE identifier, RFC 9864 — the polymorphic `EdDSA` identifier is excluded from new issuance), `kid`/`typ` mandatory inside the signed protected header (never as external fields). The capability model was split into three schema contracts — `governance/schemas/capability-claims.schema.json` (logical claims), `governance/schemas/capability-protected-header.schema.json` (decoded header), and a redefined `governance/schemas/capability-token.schema.json` (the wire artifact, surface-shape validation only) — replacing the earlier flat envelope shape. `docs/23_CAPABILITY_MODEL.md` gained an explicit Issuance profile, Verification profile, an I-JSON (RFC 7493) validation gate ahead of RFC 8785 JCS canonicalization for both the protected header and claims, a 14th capability-specific reason code (`CAPABILITY_HEADER_INVALID`), and fully worked, schema-valid, non-sensitive examples of the header, claims, and an illustrative (unsigned) wire token.
- Added `governance/schemas/` with eight JSON Schema (Draft 2020-12) contracts: action-request, policy-decision, approval, capability-claims, capability-protected-header, capability-token, audit-event, kill-switch-event. Validation performed is **structural** (valid JSON, declared Draft 2020-12 `$schema`, internal `$ref` resolution) — not full conformance or meta-schema validation; that gap is a recorded future implementation requirement.
- Extended `scripts/verify_foundation.py` to require the presence and structural validity of the new documents and schemas.
- Corrected three overclaims before this specification is considered final: self-approval prevention is enforced by the Policy Engine and Approval Service, not by JSON Schema (which cannot express cross-field comparison); audit-event canonicalization recommends RFC 8785, distinct from the Invariant Kernel's CRLF/LF file-portability normalization; the capability envelope now reflects a real JWS Compact Serialization instead of a flat, non-standard `{algorithm, key_id, payload, signature}` shape.
- No backend, database, migration, MCP, model call, service, connector, or infrastructure was implemented. No change to `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, or `governance/invariant-kernel/invariants.json`.
- Status:
  ```text
  Governance Core specification: ratified
  Governance Core implementation: not started
  ```

## 1.2.1 — 22 July 2026

- Fixed cross-platform Invariant Kernel checksum verification: the manifest checksum is now computed over a canonical (CRLF/CR normalized to LF) text representation instead of raw working-tree bytes, so Windows checkouts with `core.autocrlf=true` no longer produce a false verification failure.
- Added `.gitattributes` pinning LF line endings for Markdown, JSON, Python, YAML, TOML and shell files, with an explicit rule for `governance/invariant-kernel/*.json`.
- `scripts/verify_foundation.py` now also checks for the presence of `.gitattributes` and the explicit `eol=lf` rule for the Invariant Kernel.
- GitHub Actions verification now runs as a matrix on `ubuntu-latest` and `windows-latest`.
- No semantic, authority, or content change to the Invariant Kernel, Master Charter, Constitution, or any ADR. This is a technical portability patch only.
- The Owner's constitutional ratification of Foundation v1.2.0 (Master Charter, Constitution, ADR-0007, ADR-0008, ADR-0009) is preserved and remains in effect.

## 1.2.0 — 22 July 2026

- Disposed all Cowork audit findings H-1 through H-7.
- Added explicit Claude Cowork read-only/external-write security boundary.
- Added concrete Invariant Kernel policy bundle, schema, manifest and checksum verifier.
- Corrected Governance/Orchestrator/Audit separation.
- Added fail-closed behavior for Governance outages.
- Added provider-independent model registry.
- Added Claude Code project permissions and PreToolUse guard.
- Added GitHub Actions Foundation verification and branch-control guide.
- Added Owner ratification record and audit disposition.
- Marked Obsidian project-state note as non-authoritative mirror.


## 1.1.0 — 21 July 2026

- Added verified Claude Fable 5 and Sonnet 5 roles.
- Added Obsidian Vault architecture and independent Vault template.
- Added Graphify as a derived, rebuildable knowledge graph.
- Added model routing, cost governance and capability registry rules.
- Added controlled skill-evolution pipeline.
- Added Control Center PRD, infrastructure runbook and acceptance tests.
- Corrected Hermes baseline from v0.16.0 to v0.18.2.
- Corrected Windows guidance: Hermes supports native Windows; WSL2 is optional except for POSIX-specific features.
- Rejected “migrate all Markdown to SQLite”; governed documents remain Git/Markdown.
- Rejected mandatory 24 GB GPU for Foundation/MVP.
- Added weekly release-watch specification.

## 1.0.0 — 21 July 2026

Initial Foundation.
