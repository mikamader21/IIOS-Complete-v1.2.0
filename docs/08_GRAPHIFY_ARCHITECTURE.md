# IIOS Graphify Architecture

**Version:** 1.0.0

## Position

Graphify is a third-party derived-index tool. It maps code and documents into a queryable graph. It is useful but non-authoritative and replaceable.

## Data flow

```text
Git documents + source code + reviewed Vault notes
        → exclusion/sensitivity gate
        → local structural extraction where possible
        → optional semantic extraction
        → graphify-out
        → query/orientation
        → source verification
```

## MVP policy

- Soft nudge only: consult graph for orientation, but permit direct source reading.
- No strict graph-first hook.
- No automatic changes to CLAUDE.md/AGENTS.md.
- Pin and review the installed version during implementation.
- Keep graph output regenerable and excluded from constitutional authority.
- Exclude `.env`, secrets, databases, logs, backups, `.obsidian`, generated folders and credentials.

## Installation reference

The public package command is `uv tool install graphifyy` or equivalent pip installation. Verify the current release and hash before installation.

## Extraction modes

- Code/SQL structural extraction can be deterministic/local.
- Documents, images and transcripts may use semantic models and therefore require data-classification approval.
- For sensitive knowledge, prefer local providers or avoid semantic extraction.

## Integrity controls

- Build manifest records source paths, hashes, tool version and timestamp.
- Graph nodes retain `source_file` and stable source IDs.
- Deleted sources are removed on rebuild/update.
- Query answers cite source nodes.
- A scheduled check reports graph staleness.
- Important conclusions are verified against original files.

## Promotion policy

Graph-discovered relationship → source verification → human/agent analysis → proposed Vault note/ADR → review. Graph output never writes directly to Charter or Constitution.

## Failure behavior

If graph is missing, stale, empty or inconsistent, fall back to source search. Do not block engineering work or infer that missing nodes mean missing facts.
