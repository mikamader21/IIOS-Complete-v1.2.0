# BLOCKED

Integrations and decisions that cannot proceed without a credential, provider selection, cost approval, infrastructure, or an explicit Owner decision. Nothing in this list is scheduled — it is a registry of known blockers, referenced by `docs/TOOL_REGISTRY.md` and `MASTER_IMPLEMENTATION_PROGRAM.md`.

## Requires credentials

- **MetaApi** (Trading/Prop Firm read-only data) — no credential provisioned. `docs/TOOL_REGISTRY.md`.
- **Blockchain explorers** (API keys where required) — not provisioned. `docs/TOOL_REGISTRY.md`.
- **Market data providers** — not provisioned. `docs/TOOL_REGISTRY.md`.

## Requires provider selection

- **KMS/HSM/Vault product** for capability-signing key custody — category decided (ADR-0011), concrete provider open. `docs/23_CAPABILITY_MODEL.md` — Open questions.
- **JWKS/trusted-registry hosting** for public-key distribution — not selected. `docs/23_CAPABILITY_MODEL.md` — Open questions.
- **PostgreSQL/Supabase**: managed vs. self-hosted — open Owner decision. `PROJECT_STATE.md` — Owner decisions still required.
- **VPS provider and monthly ceiling** — open Owner decision. `PROJECT_STATE.md`.
- **JSON Schema validation library exact version pin** — library decided (`jsonschema`, `Draft202012Validator`, ADR-0011), version not pinned. `governance/schemas/README.md`.

## Requires cost approval

- **Daily and monthly model-cost hard limits** — not yet set. `PROJECT_STATE.md` — Owner decisions still required.
- Any provider integration above also implies a recurring cost decision, not just a technical one.

## Requires infrastructure

- **Hermes** — persistent runtime, not integrated. `docs/TOOL_REGISTRY.md`, `docs/HANDOFF_PROTOCOL.md`.
- **PostgreSQL/Supabase** operational database — not provisioned.
- **Secret Manager** — not provisioned.
- **Obsidian Vault live sync** — template exists (`IIOS-Vault-Template-v1.0.1`), no live, synced Vault yet.
- **Graphify live indexing** — not provisioned.

## Requires an Owner decision (non-infrastructure)

- **First read-only domain confirmation** — proposed (FundingPips/prop-firm observability, `PROJECT_STATE.md`), not yet confirmed as final.
- **Vault sync method** — separate from backup, undecided. `PROJECT_STATE.md`.
- ~~**Governance Core implementation authorization**~~ — **resolved** 23 July 2026, "AUTORIZACIÓN DEL OWNER — PHASE 3," scoped to the local skeleton only (`GOV-IMP-001`). Production implementation remains a separate future authorization.
- **Make.com mutating-action integration** — structurally Class C pending live Governance mediation; not just a technical blocker, a standing policy gate (`docs/21_GOVERNANCE_CORE_SPEC.md` case #14b).
- **Real VPS connection/modification for `HERMES-DEP-001`** — designing and preparing the deployment package is in progress and needs no further decision; connecting to or modifying an actual VPS does.
- **Source location for `ICT-KNOW-001`** — the Owner has not yet confirmed where the existing ICT source projects/documents live; the task cannot be scoped until then.
