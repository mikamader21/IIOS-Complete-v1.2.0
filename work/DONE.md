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

- In review as of this entry — see `work/NOW.md`. Will be marked complete here once merged, per `AUTONOMY_PROTOCOL.md`'s documentation-vs-implementation discipline (this file records verified outcomes, not aspirations).
