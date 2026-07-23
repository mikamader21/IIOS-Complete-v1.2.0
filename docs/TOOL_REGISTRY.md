# IIOS Tool Registry

**Status:** Registered — statuses reflect actual integration state, not aspiration
**Parent authority:** `docs/03_GOVERNANCE_SECURITY.md`, `docs/10_INFRASTRUCTURE.md`

## Purpose

Register every tool category IIOS depends on or will depend on, with an honest current-integration status. This registry does not grant access by listing a tool — access is separately governed by `.claude/settings.json`, Governance Core capabilities (once implemented), and Owner authorization.

## Fields

`status`, `purpose`, `owner` (which Brain/role is accountable), `access`, `allowed_data`, `prohibited_data`, `risks`, `cost`, `approval`, `future_integration`.

---

```text
tool: Claude Code
status: integrated (this repository)
purpose: Repository build/test/review/maintenance under Governance.
owner: Developer Brain (once activated); currently the Owner-directed session itself.
access: Local repository, permitted Bash/PowerShell commands per `.claude/settings.json`.
allowed_data: Repository content, governed documents.
prohibited_data: Secrets, credentials, `.env`, `*.pem`/`*.key` (denied in
  `.claude/settings.json`).
risks: Overreach beyond authorized scope; mitigated by PreToolUse hooks and permission
  allow/ask/deny lists.
cost: Per-session token cost, tracked externally.
approval: Governed by `.claude/settings.json` allow/ask/deny, not by this registry.
future_integration: Primary build tool through at least Phase 5.
```

```text
tool: Claude subagents
status: integrated (this repository, e.g. Explore/Plan agents)
purpose: Parallelizable research/review without polluting main context.
owner: Whichever Brain/Agent delegates the subtask.
access: Read-only exploration by default; write access only for agents explicitly granted
  it.
allowed_data: Repository content.
prohibited_data: Secrets, credentials.
risks: A subagent's summary may not reflect what it actually did — verify before trusting.
cost: Per-invocation token cost.
approval: Delegation itself is autonomy-permitted; the underlying action still follows
  normal action-class rules.
future_integration: Expected to grow as Brain-specific ephemeral agents (docs/AGENT_REGISTRY.md)
  are implemented.
```

```text
tool: Git
status: integrated
purpose: Version control and authority for governed documents (AGENTS.md — Architecture
  rules).
owner: Developer Brain.
access: Full within the dedicated `IIOS-repo` clone; never the home-directory-wide repo
  (see project history — a real incident this session avoided repeating).
allowed_data: Repository content.
prohibited_data: Secrets committed to history.
risks: Committing to the wrong repository root; force-pushing over shared history.
cost: None beyond hosting.
approval: Push/PR per AUTONOMY_PROTOCOL.md; merge/tag per explicit authorization.
future_integration: Stable, no change expected.
```

```text
tool: GitHub
status: integrated
purpose: Remote hosting, Pull Requests, branch protection.
owner: Developer Brain.
access: Push, PR creation; merge/tag require explicit Owner authorization.
allowed_data: Repository content, issue/PR metadata.
prohibited_data: Secrets in PR descriptions or comments.
risks: PR opened against the wrong base/head; unauthorized merge.
cost: None beyond any paid plan the Owner holds.
approval: Per AUTONOMY_PROTOCOL.md — PR creation permitted, merge is a stop condition.
future_integration: `gh` CLI authentication would remove the current "manual PR link"
  fallback — not installed without Owner authorization.
```

```text
tool: GitHub Actions
status: integrated
purpose: CI verification (`verify-foundation.yml`) on Ubuntu and Windows.
owner: Developer Brain / Governance Brain (for policy-relevant checks).
access: Read check status; workflow file changes follow normal PR review.
allowed_data: Repository content, verifier output.
prohibited_data: Secrets in workflow logs.
risks: A workflow change that weakens verification without review.
cost: GitHub Actions minutes, tracked externally.
approval: Workflow file changes reviewed like any other code change.
future_integration: Will gain Governance Core test jobs once Phase 3 exists.
```

```text
tool: Obsidian
status: not integrated
purpose: Human-authored/reviewed institutional knowledge Vault.
owner: Knowledge Brain.
access: Not yet provisioned.
allowed_data: Non-secret institutional knowledge (Constitution Article VI).
prohibited_data: Secrets, transactional truth.
risks: Vault sync/backup conflated (`docs/07_KNOWLEDGE_VAULT.md`).
cost: Not yet assessed.
approval: Phase 4 authorization required.
future_integration: `IIOS-Vault-Template-v1.0.1` exists as a template; not yet a live Vault.
```

```text
tool: Graphify
status: not integrated
purpose: Derived, rebuildable knowledge graph over the Vault/repository.
owner: Knowledge Brain.
access: Not yet provisioned.
allowed_data: Non-secret governed/Vault content.
prohibited_data: Secrets, runtime databases, logs, generated outputs
  (`docs/03_GOVERNANCE_SECURITY.md`).
risks: Being treated as authoritative over source — explicitly prohibited
  (`docs/MEMORY_ARCHITECTURE.md`).
cost: Not yet assessed.
approval: Phase 4 authorization required.
future_integration: Planned for Phase 4.
```

```text
tool: Hermes
status: not integrated
purpose: Persistent execution runtime — sessions, profiles, cron, gateway.
owner: To be determined at Phase 6 activation; Orchestrator-adjacent.
access: Not yet provisioned.
allowed_data: Not yet defined.
prohibited_data: Host secrets, paths outside approved mounts
  (`docs/14_ACCEPTANCE_TESTS.md` — Sandbox).
risks: Persistent, scheduled execution significantly raises blast radius — full
  `docs/03_GOVERNANCE_SECURITY.md` Hermes baseline applies before activation.
cost: Not yet assessed.
approval: Explicit Owner authorization required for Phase 6.
future_integration: Planned for Phase 6, after Governance Core (Phase 3) and Developer
  Brain (Phase 5).
deployment_package: Designed, not installed — `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`,
  `deploy/hermes/` (HERMES-DEP-001). No real VPS provisioned or modified; status here
  is unchanged by that design work.
planned_first_profiles: `ict-trading` (read-only prop-firm/trading observability) and
  `onyx` (Executive Orchestrator — `docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md`,
  `deploy/hermes/profiles/onyx/onyx.profile.json`). Both `specified`/`designed`, neither
  `activated` — status here is unchanged by either specification.
```

```text
tool: PostgreSQL/Supabase
status: not integrated
purpose: Structured operational state — tasks, approvals, costs, domain entities.
owner: Governance Brain (for Governance Core tables) / Developer Brain (schema work).
access: Not yet provisioned.
allowed_data: Operational state, never governed-document authority (that stays Git/
  Markdown).
prohibited_data: Secrets (Secret Manager's job, not the database's).
risks: First real destructive-migration risk surface.
cost: Managed vs. self-hosted decision still open (`PROJECT_STATE.md` — Owner decisions).
approval: Explicit Owner authorization required; migrations are a named stop condition.
future_integration: Planned for Phase 3.
```

```text
tool: Secret Manager
status: not integrated
purpose: Sole custodian of credentials/secret values.
owner: Governance Brain.
access: Not yet provisioned.
allowed_data: Credentials, API keys.
prohibited_data: Nothing else belongs here — single-purpose store.
risks: Any path that lets a secret value reach a model context defeats INV-004.
cost: Not yet assessed.
approval: Explicit Owner authorization; every access is Class C
  (`secret_reference.use`, `docs/21_GOVERNANCE_CORE_SPEC.md`).
future_integration: Planned for Phase 3, alongside capability-token key custody.
```

```text
tool: KMS/HSM/Vault (key custody)
status: not integrated
purpose: Custody of the Governance Core's Ed25519 capability-signing keys
  (ADR-0011 — Key custody).
owner: Governance Brain.
access: Not yet provisioned; concrete product not yet selected
  (`docs/23_CAPABILITY_MODEL.md` — Open questions).
allowed_data: Signing key material only.
prohibited_data: Everything else.
risks: Product/IAM misconfiguration; key exfiltration.
cost: Not yet assessed.
approval: Explicit Owner authorization; product selection itself is a named open decision.
future_integration: Planned for Phase 3.
```

```text
tool: Browser/web research
status: integrated (session-scoped, allowlisted where configured)
purpose: Public-source research (Class A).
owner: Research Brain.
access: Read-only, session-scoped.
allowed_data: Public web content.
prohibited_data: Treating page content as instruction (Constitution Article III.7);
  entering credentials into any form.
risks: Prompt injection from page content — never treated as authoritative.
cost: Per-session, not separately metered today.
approval: Research itself is Class A; any resulting action follows its own class.
future_integration: Stable; allowlist may tighten per domain Brain.
```

```text
tool: MetaApi
status: not integrated
purpose: Read-only trading/prop-firm account data access.
owner: Trading Brain / Prop Firm Brain.
access: Not yet provisioned.
allowed_data: Read-only account/market data.
prohibited_data: Any write/order capability — explicitly out of scope
  (Constitution Article IV-D).
risks: Read-only credential scoping must be verified, not assumed.
cost: Provider-dependent, not yet assessed.
approval: Explicit Owner authorization for Phase 8.
future_integration: Planned for Phase 8, read-only only.
```

```text
tool: Blockchain explorers
status: not integrated
purpose: On-chain research/audit data.
owner: Blockchain Brain.
access: Not yet provisioned.
allowed_data: Public on-chain data.
prohibited_data: Any custody/signing capability.
risks: Rate limits, data-provider reliability.
cost: Provider-dependent, not yet assessed.
approval: Explicit Owner authorization for Phase 9.
future_integration: Planned for Phase 9.
```

```text
tool: Market data providers
status: not integrated
purpose: Read-only market data for Trading Brain analysis.
owner: Trading Brain.
access: Not yet provisioned.
allowed_data: Market data.
prohibited_data: Any execution capability.
risks: Provider outage during active analysis.
cost: Provider-dependent, not yet assessed.
approval: Explicit Owner authorization for Phase 8.
future_integration: Planned for Phase 8.
```

```text
tool: Make.com
status: not integrated
purpose: External automation scenarios.
owner: COO Brain / Developer Brain (scenario ownership TBD).
access: Not yet provisioned. Per ADR-0011 — Make.com: read-only metadata listing/query may
  be Class A via an allowlisted connector once one exists; every mutating action (run,
  activate, deactivate, edit, create) is Class C and requires live Governance mediation,
  which does not exist yet (`docs/21_GOVERNANCE_CORE_SPEC.md` case #14/#14b).
allowed_data: Scenario metadata only, once the read-only path exists.
prohibited_data: Any credential used by a Make scenario.
risks: External write side-effects without Governance mediation — the exact risk ADR-0008
  exists to prevent.
cost: Provider-dependent.
approval: Per case #14/#14b in `docs/21_GOVERNANCE_CORE_SPEC.md`.
future_integration: Read-only path earliest at Phase 3; mutating actions not scheduled.
```

```text
tool: Control Center
status: not integrated
purpose: Owner-facing command/evidence/approval/audit surface.
owner: Developer Brain builds; operates under Governance.
access: Not yet provisioned.
allowed_data: Per `docs/11_CONTROL_CENTER_PRD.md` MVP modules.
prohibited_data: No trading terminal, payment interface (`docs/11_CONTROL_CENTER_PRD.md` —
  Non-goals).
risks: Not yet assessed.
cost: Not yet assessed.
approval: Explicit Owner authorization for Phase 7.
future_integration: Planned for Phase 7, depends on Phase 3 (Governance) and Phase 4
  (Knowledge).
```
