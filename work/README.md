# Work State

Four files track the autonomous cycle's live state, per `AUTONOMY_PROTOCOL.md`:

- `NOW.md` — what is currently in progress or in review.
- `NEXT.md` — the next authorized task, once its dependencies clear.
- `BLOCKED.md` — work that cannot proceed without a credential, provider, cost approval, infrastructure, or an Owner decision.
- `DONE.md` — a running record of completed phases/tasks, for continuity across sessions.

These are operational state, not authority — `PROJECT_STATE.md` and `MASTER_IMPLEMENTATION_PROGRAM.md` remain the authoritative phase record. `work/` exists so a new session can resume without re-deriving context from scratch.
