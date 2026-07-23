# IIOS Kill Switch Specification

**Version:** 0.1.0
**Status:** Specified, not implemented
**Parent:** `docs/21_GOVERNANCE_CORE_SPEC.md`, Constitution Article VIII, `docs/03_GOVERNANCE_SECURITY.md` Emergency response
**Schema:** `governance/schemas/kill-switch-event.schema.json`

## Purpose

Give the Owner a way to stop IIOS activity that does not depend on Hermes, the Orchestrator, or the Governance API itself being healthy (Constitution Article VIII: "Owner can stop gateways/workers, revoke keys, block egress, disable schedulers, freeze connectors and restore backups without depending on Hermes responsiveness").

## Levels

| Level | Scope | Typical trigger |
|---|---|---|
| **L1** | Stop one task | A single task is misbehaving or its cost/risk profile changed mid-run |
| **L2** | Stop one runtime/profile | A Hermes profile or agent session is compromised or looping |
| **L3** | Stop all workers | Suspected systemic issue across execution, not isolated to one profile |
| **L4** | Revoke credentials and block egress | Suspected credential compromise or data exfiltration risk |
| **L5** | Total emergency isolation | Any condition where the Owner cannot yet determine scope and wants everything stopped |

Levels are not strictly nested prerequisites — the Owner may invoke any level directly. Higher levels include the effects of lower ones for the resources in scope (e.g. L4 also stops the affected workers, it does not require L1-L3 to be triggered first).

## Activation

Activation authentication is **independent of Governance API availability** — this is the entire point of a kill switch. `kill-switch-event.schema.json#/auth_method` is `owner_session`, `owner_out_of_band` (e.g. a channel that does not route through the same infrastructure being killed), or `delegated_token`. Activation at any level requires an Owner-authenticated identity; delegation to a non-Owner Approval Authority is not permitted for activation (only recovery may involve a delegated identity, and only if the Owner has explicitly ratified that delegation).

## Recovery

Recovery is a distinct, explicitly authenticated action (`action: recover` in `kill-switch-event.schema.json`), never automatic and never time-based. A recovery event references the `activate` event it closes (`recovery_of_event_id`). Recovery from L4/L5 additionally requires: confirmation that the triggering condition is understood and resolved, credential rotation completed (if L4/L5), and a review of the audit trail covering the incident window before resuming any Class B/C activity.

## Effects by level

- **Revoke capabilities**: L2 revokes capabilities scoped to the affected profile; L3-L5 revoke all outstanding capabilities.
- **Stop schedulers**: L2+ disables cron/scheduled triggers for the affected scope; L3-L5 disables all schedulers.
- **Block connectors**: L4-L5 freeze all external connectors (mirrors the existing Cowork write-connector freeze pattern in ADR-0008, extended to every connector, not just Cowork's).
- **Egress block**: L4-L5 block outbound network access at the infrastructure level, not merely at the application layer, so a compromised process cannot route around the block.
- **Preserve logs**: every level. `kill-switch-event.schema.json#/logs_preserved` is a schema `const: true` — no level may delete or truncate audit/log storage; a kill switch that could erase its own evidence would defeat Constitution Article III.2.

## Periodic testing

**Resolved by Owner decision** (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md` — Kill Switch test cadence), superseding the quarterly/annual proposal previously open here:

- **L1, L2**: monthly drill, staging.
- **L3**: quarterly drill, staging.
- **L4**: semiannual drill in staging, plus an annual tabletop exercise covering production.
- **L5**: annual tabletop exercise.
- A **real L5 activation drill** (not a tabletop) requires separate, explicit Owner authorization, independent of this standing cadence.

Each drill produces its own `kill_switch_activated`/`kill_switch_recovered` event pair so the drill itself is auditable and distinguishable from a real incident (a `reason` field describing it as a drill).

## Relation to Governance and Audit

A kill-switch activation is not routed through the normal Policy Engine evaluation path — it is a separate, higher-priority control specifically so it still works when Governance itself is the thing misbehaving or unreachable. Once activated, however, its state (which scopes are killed) becomes an input to the Policy Engine: any action-request whose scope overlaps an active kill-switch level resolves to `deny` (`KILL_SWITCH_ACTIVE`), and this check happens before normal policy evaluation, not after.

## Test cases specific to the Kill Switch

| Scenario | Setup | Expected outcome |
|---|---|---|
| L1 during Governance outage | Governance API unreachable, Owner activates L1 for one task | Activation succeeds via the independent auth path; task stopped; event queued for the audit chain and appended once Audit is reachable |
| Scope-matched deny | L2 active for profile P, new request from profile P | `policy_decision` deny (`KILL_SWITCH_ACTIVE`) before any rule evaluation |
| Out-of-scope request | L2 active for profile P, new request from unrelated profile Q | Normal evaluation proceeds; not blocked by P's kill switch |
| Attempted self-recovery by a runtime | Any non-Owner actor attempts a `recover` action | Rejected; `auth_method` for activation/recovery never accepts a `runtime` or `orchestrator` actor type |
| Log deletion attempt during L5 | Any component attempts to delete/truncate audit storage while L5 is active | Rejected structurally; `logs_preserved` is non-negotiable at every level |
| Drill vs. real incident | Scheduled monthly L1/L2 drill (ADR-0011 cadence) | Same event schema, `reason` marks it as a drill; does not require incident postmortem, still fully audited |
