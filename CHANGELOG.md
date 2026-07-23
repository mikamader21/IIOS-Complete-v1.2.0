# Changelog

## Unreleased — Governance Core specification

- Added `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`: technical specification of the Governance API, Action Classifier, Orchestrator Boundary, Policy Engine, Capability Model, Approval Model, Audit Event Model, and Kill Switch.
- Added `docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md` recording the boundary decisions and discarded alternatives.
- Added `governance/schemas/` with six JSON Schema (Draft 2020-12) contracts: action-request, policy-decision, approval, capability-token, audit-event, kill-switch-event.
- Extended `scripts/verify_foundation.py` to require the presence and JSON validity of the new documents and schemas.
- No backend, database, migration, MCP, model call, service, or external connector was implemented. No change to `docs/00_MASTER_CHARTER.md`, `docs/01_CONSTITUTION.md`, or `governance/invariant-kernel/invariants.json`.
- Status: **Governance Core: specified, not implemented.** Pending Owner review and ratification of ADR-0010 before any implementation work begins.

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
