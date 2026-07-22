# IIOS Research Audit and Corrections

**Version:** 1.2.0

## Accepted from supplied reports

External governance, read-only finance, Docker isolation, source-of-truth discipline, hard cost/loop limits, staged implementation and procedural skills.

## Corrections

- Hermes v0.16.0 is not the latest verified release; v0.18.2 is the cutoff baseline.
- Hermes supports native Windows 10/11; WSL2 is optional for POSIX-specific features.
- Markdown is not replaced by SQLite. Governed documents remain Git/Markdown; databases store operational state.
- A 24 GB GPU is not required for Foundation/API-based MVP.
- Prompt-caching savings depend on provider/model/workload and are not guaranteed as a universal 80–95% budget assumption.
- Graphify public version information can change quickly; verify at installation and pin the tested release.
- ReAct history in the transcription is dated; modern IIOS uses structured tool calling plus deterministic authorization.

## New verified additions

- Claude Fable 5 exists and is Mythos-class; it is an escalation model, not system authority.
- Claude Sonnet 5 is appropriate as a candidate daily agentic model.
- Claude Code can import AGENTS.md from CLAUDE.md and treats instructions as context, not enforcement.
- Obsidian Vault is local Markdown; sync is not backup.
- Graphify can create a local queryable knowledge graph, but remains derived.

## Evidence rule

Research becomes architecture only after primary source, date/version, limitation, IIOS implication and ADR acceptance.
