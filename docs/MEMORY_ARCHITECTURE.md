# IIOS Memory Architecture

**Status:** Specified, not implemented
**Parent authority:** `AGENTS.md` — Context rules, Constitution Article VI

## Purpose

Define the memory types IIOS Brains/Agents will use and where each is stored, before any of it is wired up. Memory is advisory and scoped by default; authority lives in governed Git/Markdown documents, never in memory of any kind (Constitution Article VI).

## Memory types

```text
Working Memory       — current task/session context, ephemeral
Episodic Memory       — task/session history for a persistent role (docs/AGENT_REGISTRY.md)
Semantic Knowledge     — curated facts/research with provenance
Procedural Memory      — established how-to patterns for a role
Owner Profile          — OWNER_PROFILE.md, stable professional/operational context
Project State          — PROJECT_STATE.md, verified current phase
Operational State       — structured runtime state (tasks, approvals, costs)
Audit Memory            — append-only evidence (docs/25_AUDIT_EVENT_MODEL.md)
```

## Storage assignment

```text
Git/Markdown
  → authority, specifications, and decisions (Charter, Constitution, Kernel, ADRs,
    Governance Core specs, OWNER_PROFILE.md, PROJECT_STATE.md)

Obsidian
  → human knowledge, research, and linked notes (Semantic Knowledge, human-reviewed)

Graphify
  → derived relationship graph (never authoritative, always rebuildable)

PostgreSQL/Supabase
  → structured operational state (Operational State)

Hermes profile memory
  → per-runtime operational continuity (Episodic/Procedural, scoped to a Hermes profile,
    once Phase 6 exists)

Vector retrieval
  → semantic recall index (a derived index over Semantic Knowledge, not a memory type
    itself)
```

## Rules

- **Git is the authoritative source for ratified documents.** No other memory type may override a governed Git/Markdown document (`AGENTS.md` — Architecture rules).
- **Graphify is derived, never authority.** A Graphify result must link back to a checkable source; a stale or failed graph falls back to source reading (`docs/14_ACCEPTANCE_TESTS.md` — Knowledge integrity).
- **Vector stores are derived indices**, not a source of truth — the same rule as Graphify, applied to embeddings-based retrieval.
- **Model memory (a model's own context/training) does not substitute for a record.** A claim needing to be checked later must exist in Git, Obsidian, or Operational State — not only in a transcript.
- **Every memory item carries provenance and a date** — what it is, where it came from, and when it was true. An undated or unsourced item is treated as advisory only.
- **Sensitive information must be classified.** `OWNER_PROFILE.md` explicitly excludes family/medical/intimate data by default (Scope section); any future memory item touching such data needs the same explicit-authorization discipline.
- **The Owner controls deletion and retention.** No Brain or Agent unilaterally decides what is forgotten from Semantic Knowledge, Episodic Memory tied to the Owner, or Audit Memory (the last is additionally append-only and cannot be deleted at all, Constitution Article III.2).
- **Do not duplicate the entire project history into every prompt.** Working Memory pulls only what the current task needs; Semantic/Episodic retrieval is scoped, not exhaustive (`AGENTS.md` — Mandatory reading protocol: "Retrieve only relevant Vault/graph context; do not load the entire knowledge base").

## What does not exist yet

No PostgreSQL/Supabase instance, no live Graphify index, no vector store, and no Hermes profile memory exist today. `OWNER_PROFILE.md` and `PROJECT_STATE.md` are the only memory types with real, populated content as of this phase; everything else in this document is a storage contract for future phases (Phase 3 for Operational/Audit Memory, Phase 4 for Obsidian/Graphify/vector retrieval, Phase 6 for Hermes profile memory).
