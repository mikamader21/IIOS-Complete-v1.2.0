@AGENTS.md
@PROJECT_STATE.md
@AUTONOMY_PROTOCOL.md

# Claude Code-specific instructions

- At session start (Phase 2 onward): read `PROJECT_STATE.md`, `AUTONOMY_PROTOCOL.md`, `work/NOW.md`, `BACKLOG.md`, then select the highest-priority `ready` task with resolved dependencies — see `AGENTS.md` — "Autonomous session start."
- Do not ask the Owner what to do next while `BACKLOG.md` contains an authorized `ready` task; stop only at a real gate in `AUTONOMY_PROTOCOL.md`.
- Do not interpret documentation status (`specified`, `cataloged`, `not_implemented`) as implementation status.
- Use plan mode for architecture, security, permissions, data models, deployment, model routing, Vault/Graphify integration or changes spanning more than three files.
- Read applicable governed documents before editing.
- Prefer small, reviewable commits grouped by purpose.
- Run narrow tests first, then the broad suite.
- Treat CLAUDE.md as guidance, not enforcement; use permissions, hooks and CI for hard boundaries.
- Do not add agents, skills, MCP servers, Graphify hooks or infrastructure services without an accepted ADR.
- Do not place business authority or financial rules only here.
- Never modify Charter, Constitution or AGENTS.md as a side effect.
- Update PROJECT_STATE.md only with verified outcomes.
- Use Graphify for orientation when available, then verify important conclusions against source files.
