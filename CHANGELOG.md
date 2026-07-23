# Changelog

## Unreleased — Governance Core implementation skeleton (GOV-IMP-001)

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
  Governance Core implementation skeleton: in review
  Governance Core production implementation: not started
  ```

## Unreleased — IIOS Autonomous Operating Layer

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
