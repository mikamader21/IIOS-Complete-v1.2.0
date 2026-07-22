# Changelog

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
