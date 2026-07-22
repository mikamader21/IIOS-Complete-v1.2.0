# IIOS Context and Memory Architecture

**Version:** 1.2.0

## Authority map

| Information | Authority |
|---|---|
| Purpose/authority | Charter |
| Non-negotiable rules | Constitution |
| Shared operational instructions | AGENTS.md |
| Claude-specific workflow | CLAUDE.md |
| Verified current state | PROJECT_STATE.md |
| Architecture/security | docs + ADRs |
| Institutional knowledge | Obsidian Vault with metadata |
| Procedures | Reviewed skills/workflows |
| Operational state | PostgreSQL/Supabase |
| Secrets | Secret Manager |
| Large artifacts | Object storage |
| Derived relations | Graphify |
| Generated runtime memory | Advisory only |

## Context files

Hermes priority: `.hermes.md/HERMES.md` → `AGENTS.md` → `CLAUDE.md`; only the first project-context type loads. Therefore no root `.hermes.md` in Foundation.

Claude Code reads `CLAUDE.md`, which imports `AGENTS.md`. Keep root instruction files concise; scoped rules load for relevant paths.

`SOUL.md` lives in `HERMES_HOME` and defines personality only.

## Memory classes

- Constitutional: Charter/Constitution/ADRs.
- Institutional: architecture, decisions, postmortems and reviewed Vault notes.
- Operational: tasks, approvals, costs and connector state.
- Procedural: reviewed skills/workflows.
- Semantic: indexed sources with provenance.
- Episodic: session summaries, advisory.
- Personalization: preferences that do not alter authority.
- Temporary: expiring scratch context.

## Promotion flow

```text
Observation → evidence → candidate learning → validation → review
→ destination selection → versioned update → audit
```

Constitutional, financial and permission logic cannot be autonomously promoted.

## Retrieval rules

Retrieve relevant context only; include source, timestamp, authority and sensitivity; prefer exact policy sections; reject stale data; isolate domains; never index secrets; record evidence used for sensitive decisions.

## Claude auto-memory

Claude Code auto-memory is useful for build/debug patterns, but it is local, advisory and auditable. It cannot override repository instructions. Review with `/memory`; disable or clear when contaminated.

## Hermes memory

Hermes memory, session history, skills and optional user modeling remain per profile. Profile state separation does not equal sandboxing.

## Context efficiency

Keep startup files stable, move detailed procedures to skills, use progressive subdirectory context, summarize sessions, deduplicate retrieval and cache stable prefixes.
