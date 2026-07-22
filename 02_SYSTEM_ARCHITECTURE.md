@AGENTS.md
@PROJECT_STATE.md

# Claude Code-specific instructions

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
