# IIOS Claude ↔ Hermes Handoff Protocol

**Status:** Specified, not implemented — Hermes is not integrated (`docs/TOOL_REGISTRY.md`)
**Parent authority:** `AGENTS.md` — Tool roles

## Purpose

Define the division of labor between Claude (build-time) and Hermes (run-time) before Hermes is integrated (`MASTER_IMPLEMENTATION_PROGRAM.md` Phase 6), and specify the contract a task handoff between them will use.

## Claude

- Builds.
- Modifies code.
- Creates tests.
- Performs refactors.
- Opens Pull Requests.
- Improves architecture.

Claude operates build-time, under `AUTONOMY_PROTOCOL.md`, inside version-controlled branches with CI verification. Claude does not run persistently and does not hold scheduled/standing execution.

## Hermes

- Will execute persistent tasks.
- Schedulers.
- Monitoring.
- Operational workflows.
- Context recovery.
- Profile coordination.

Hermes operates run-time, persistently, under whatever Governance Core capability model exists at the time of its integration (Phase 6, after Phase 3). Hermes does not modify IIOS's own source code or documentation — that remains Claude's (and eventually Developer Brain's) role.

## Handoff artifact (future contract, not implemented)

```text
handoff_id           — unique identifier for this handoff
source                — the runtime handing off (e.g. "claude-code")
target                — the runtime receiving (e.g. "hermes-profile:trading-monitor")
task_id               — the BACKLOG.md or operational task this handoff serves
objective              — what the target runtime is being asked to do
context_refs           — pointers to relevant docs/state, not inlined full history
allowed_actions        — explicit allowlist, never default-allow
prohibited_actions     — explicit denylist for this handoff
required_skills        — from docs/SKILL_CATALOG.md
budget                 — cost ceiling for the handed-off task
deadline               — time bound, if any
approval_state         — not_required | pending | approved | rejected | expired | revoked
                          | consumed (mirrors docs/24_APPROVAL_MODEL.md's states)
expected_outputs        — what completion looks like
correlation_id          — propagated per docs/21_GOVERNANCE_CORE_SPEC.md's traceability rule
```

This mirrors the Governance Core's action-request/capability shape deliberately — a handoff to Hermes is, functionally, a scoped delegation and should be governed the same way once Governance Core exists, not through a separate parallel trust mechanism.

## Rules

- A handoff never grants Hermes more scope than the issuing Claude session itself holds.
- A handoff's `allowed_actions` is never open-ended ("do whatever is needed") — it is an explicit list.
- Hermes does not receive standing credentials through a handoff; per-task capabilities only, once Governance Core capability issuance exists.
- A handoff to Hermes for anything Class C or D follows the same Approval Service path any other Class C/D request would (`docs/24_APPROVAL_MODEL.md`) — Hermes does not bypass approval by virtue of being the execution runtime.

## Status

Not implemented. Hermes is not integrated (`docs/TOOL_REGISTRY.md`). This document specifies the contract Phase 6 will build against.
