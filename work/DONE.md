# DONE

Completed phases and tasks, for continuity across sessions. `MASTER_IMPLEMENTATION_PROGRAM.md` remains the authoritative phase record; this is a flat log.

## Phase 0 — Foundation

- Master Charter, Constitution, Invariant Kernel ratified.
- Repository controls: `.claude/settings.json` permissions, PreToolUse guard, branch protection groundwork, `.github/workflows/verify-foundation.yml`.
- Cross-platform Invariant Kernel checksum fix (v1.2.1): `.gitattributes`, canonical (CRLF/CR-to-LF) hashing, Windows + Ubuntu CI matrix.
- Tag `v1.2.1` published, dereferencing the ratified Foundation baseline.
- Corrupted pre-Foundation `main` state preserved for recovery at `archive/corrupt-main-81e830e` (never deleted).

## Phase 1 — Governance Core Specification

- `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`: Governance API, Action Classifier, Policy Engine, Approval Service, Capability model, Audit Event model, Kill Switch, Orchestrator Boundary, 20 mandatory decision cases.
- Six (then eight, after the capability-envelope correction) JSON Schema (Draft 2020-12) contracts under `governance/schemas/`.
- ADR-0010 (Governance Core Boundaries) and ADR-0011 (Governance MVP Owner Decisions) — both **Ratified**.
- Capability cryptographic profile corrected to real JWS Compact Serialization, `alg: Ed25519` (RFC 9864), `kid`/`typ` mandatory in the protected header; claims/header/wire-token split into three schema contracts; RFC 8785 JCS + I-JSON (RFC 7493) validation gate specified for issuance.
- Tag `v1.3.0` published, dereferencing the ratified Governance Core specification baseline.
- Merged branches cleaned up (`docs/ratify-governance-core`, `feature/governance-core-spec` deleted, local and remote, after confirming green CI).

## Phase 2 — Autonomous Operating Layer

- `AOL-001` merged: PR #6, commit `83c2c73`, merge commit `1f4ea9762cb5a2060cc38746af057c63ef2286a7`. CI verified green. `OWNER_PROFILE.md`, `AUTONOMY_PROTOCOL.md`, `MASTER_IMPLEMENTATION_PROGRAM.md`, `BACKLOG.md`, 11 registry/protocol docs under `docs/`, `work/` state files.
- Branch `feature/autonomous-operating-layer` deleted (local and remote) after confirming the merge.

## Phase 3 — Governance Core Implementation

- `GOV-IMP-001` merged: PR #7, commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`. CI verified green — 4/4 checks (`verify` ubuntu/windows, `governance-tests` ubuntu/windows), run `30047219545`.
- `src/iios_governance/`: local, deterministic, in-memory reference implementation of the ratified Governance Core specification — domain, application, ports, memory and filesystem adapters. 133 tests passing, 97% coverage, clean ruff/mypy. No production cryptography (`DisabledSignatureVerifier` fails closed), no database, no external providers, no action execution.
- `governance/schemas/policy-bundle.schema.json` + `governance/policy-bundles/mvp/` (checksum-protected, 20 rules). `docs/ADR/ADR-0012-POLICY-BUNDLE-FORMAT.md` — **Proposed** (not yet ratified).
- `docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md` written.
- CI extended with a `governance-tests` job (ubuntu-latest + windows-latest); pre-existing `verify` job unchanged.
- Branch `feature/governance-core-skeleton` deleted (local and remote) after confirming the merge.
- Status:
  ```text
  Governance Core specification: ratified
  Governance Core implementation skeleton: done
  Governance Core production implementation: not started
  ```
