# IIOS Hermes VPS Deployment Package (HERMES-DEP-001)

**Status:** Design/preparation complete. No real VPS provisioned, connected to, or modified. Hermes remains **not integrated** (`docs/TOOL_REGISTRY.md`).
**Parent authority:** `docs/03_GOVERNANCE_SECURITY.md` (Hermes baseline), `docs/10_INFRASTRUCTURE.md` (VPS MVP direction), `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`, `docs/HANDOFF_PROTOCOL.md`, `MASTER_IMPLEMENTATION_PROGRAM.md` Phase 6.

## Scope

This document and the package under `deploy/hermes/` cover exactly the eighteen deliverables listed for `HERMES-DEP-001` in `BACKLOG.md`. Every artifact is a template, script, or document reviewed and version-controlled ahead of any real infrastructure — none has been executed against a host. Connecting to or modifying a real VPS is a separate, explicit Owner decision (`work/BLOCKED.md`) and a separate task.

## 1. VPS threat model

| Threat | Vector | Mitigation in this package |
|---|---|---|
| Remote compromise via exposed service | Public Hermes/DB/gateway port | No public listener; private-network-only access (§3, `deploy/hermes/firewall/`) |
| Lateral movement after a profile is compromised | Shared filesystem across profiles | Per-profile directory ownership and permissions (§4, §5) |
| Secret exfiltration | Committed credentials, forwarded env vars, verbose logs | No secret ever committed; `EnvironmentFile=` injection; empty forwarded-env allowlist by default (`deploy/hermes/secrets/`) |
| Data exfiltration via egress | Unrestricted outbound traffic from a compromised process | Default-deny egress allowlist (§7, `deploy/hermes/firewall/egress-allowlist.md`) |
| Unbounded command execution | Hermes `terminal.backend` running arbitrary host commands | Docker terminal backend, explicit `terminal.cwd`, `terminal.home_mode` never `full` (§6) |
| Silent service failure | No supervision, no alerting | systemd `Restart=on-failure`, health-check timer (§10, §13) |
| Unrecoverable data loss | No backup, or an untested backup | Encrypted, scheduled, restore-tested backups (§9) |
| Privilege escalation from Hermes to host | Hermes running as root or with `sudo` | Dedicated unprivileged `hermes` user, no `sudo` grant (§2) |
| Unbounded financial/order action | A future trading profile executing a real order | `ict-trading` profile is read-only only; no order endpoint exists in its capability scope, independent of and in addition to Constitution Article IV-D (§16) |
| Untested or silent rollback | Update breaks the service with no recovery path | Pinned-version updates, documented and rehearsed rollback runbook (§11, §17) |

Residual risk: this threat model covers the deployment package itself. It does not cover Hermes' own application-level vulnerabilities (patched via the existing `docs/10_INFRASTRUCTURE.md` upgrade policy) or Governance Core's production cryptography, which remains explicitly unimplemented (`docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md`).

## 2. Unprivileged service user

A single dedicated system user, `hermes`, owns every Hermes process and file. It is created with a locked password, no login shell of consequence (`/usr/sbin/nologin`), no `sudo` group membership, and no SSH key. See `deploy/hermes/scripts/create-service-user.sh`.

## 3. Directory structure

See `deploy/hermes/directory-layout.md` for the full tree and `deploy/hermes/scripts/bootstrap-directories.sh` for the template that creates it. Top level: `/opt/hermes/{core,profiles,backups,logs}`, each owned `hermes:hermes`.

## 4. Filesystem isolation

Each profile directory (`/opt/hermes/profiles/<profile>/`) is `0750`, owned by `hermes`, and is the only path that profile's Compose service bind-mounts. No profile's Compose service mounts another profile's directory, `/opt/hermes/core/secrets/`, or any host path outside `/opt/hermes/`. This is the host-level backstop `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` decision 6 adds on top of Hermes' own profile isolation.

## 5. `terminal.cwd` / `terminal.home_mode`

Every Hermes profile configuration fixes `terminal.cwd` to that profile's scoped directory (`/opt/hermes/profiles/<profile>/workspace`) and sets `terminal.home_mode` to a restricted, profile-scoped value — never a mode that exposes the full host home directory. See `deploy/hermes/profiles/ict-trading.profile.json` for a worked example. This directly satisfies `docs/03_GOVERNANCE_SECURITY.md`'s "Set explicit `terminal.cwd`" baseline and the Sandbox acceptance test in `docs/14_ACCEPTANCE_TESTS.md`.

## 6. Terminal backend

`terminal.backend: docker` for every profile (`docs/10_INFRASTRUCTURE.md`), independent of Hermes-in-Docker (§ Docker distinction, same document). Forwarded environment variable allowlist is empty by default per profile, matching `docs/03_GOVERNANCE_SECURITY.md`.

## 7. Egress allowlist

Default-deny outbound; only the private tunnel and the specific hosts a profile's Hermes needs (model-provider APIs, package registries during install/update) are allowlisted. Full design and the destinations table: `deploy/hermes/firewall/egress-allowlist.md`.

## 8. Firewall design

UFW, default-deny inbound and outbound. Inbound: SSH from the operator's known network only (or disabled in favor of the Tailscale/tunnel interface), plus the tunnel interface itself. No inbound rule for Hermes/DB/gateway ports on the public interface — access to those is tunnel-only. Template: `deploy/hermes/firewall/apply-ufw-rules.sh` (not executed by this task).

## 9. Backups

A systemd timer (`hermes-backup.timer` → `hermes-backup.service`) runs a file-level backup of `/opt/hermes/{core,profiles}` (excluding `secrets/` — secrets are backed up, if at all, through the eventual KMS/HSM/Vault product's own mechanism, not this path) to an external, encrypted destination. Restore procedure: `deploy/hermes/runbooks/BACKUP_RESTORE.md`.

## 10. Logs

Hermes container logs use the `json-file` Docker log driver with rotation (`max-size`/`max-file` set in Compose); systemd unit logs go to the journal (`journalctl -u hermes-*`). No log path is world-readable; the `hermes` user owns `/opt/hermes/logs/`.

## 11. Health checks

`hermes-healthcheck.timer` → `hermes-healthcheck.service` runs a lightweight liveness check (gateway responds on its private-network port, Compose services report `healthy`) on a short interval and logs failures to the journal — it does not restart anything itself; `Restart=on-failure` on the Compose-supervising unit handles recovery. Detail: `deploy/hermes/runbooks/HEALTH_CHECKS.md`.

## 12. Update / rollback procedure

Follows `docs/10_INFRASTRUCTURE.md`'s upgrade policy verbatim: release watch → read notes/security → staging backup → pinned upgrade → tests → observation window → production approval → rollback readiness. Concrete steps: `deploy/hermes/runbooks/UPDATE_ROLLBACK.md`.

## 13. Profile separation

Profiles isolate both Hermes application state (existing baseline) and, per this package, host filesystem access (§4), `terminal.cwd`/`terminal.home_mode` (§5), and Compose bind mounts. A profile cannot read, write, or execute inside another profile's directory.

## 14. Secret injection design

No real secret exists in this package. `deploy/hermes/secrets/env.template` lists every environment variable a profile's Compose service expects, each set to a placeholder. The real file (`.env`, git-ignored, `0600`, owned `hermes:hermes`) is populated out-of-band by the Owner (or, later, by whatever secret-management product is selected — `work/BLOCKED.md`) and referenced by the systemd unit's `EnvironmentFile=` directive. No script in this package reads or prints a secret value. Detail: `deploy/hermes/secrets/README.md`.

## 15. `ict-trading` profile package

`deploy/hermes/profiles/ict-trading.profile.json` — the first Hermes profile, scoped read-only (account status, balance/equity, drawdown/rules, history, alerts, calendar; no order endpoint), matching `PROJECT_STATE.md`'s proposed first domain. It carries no standing capability — every action still requires a live Governance decision once Hermes is actually integrated (Phase 6), which this task does not perform.

## 16. Installation runbook

`deploy/hermes/runbooks/INSTALL.md` — step-by-step, from a bare Ubuntu LTS VPS to a running, health-checked Hermes gateway with the `ict-trading` profile provisioned but not yet activated. Not executed by this task.

## 17. Uninstall / rollback runbook

`deploy/hermes/runbooks/UNINSTALL_ROLLBACK.md` — full teardown (stop services, remove Compose stack, optionally purge `/opt/hermes/`) and a partial-rollback path (revert to the previous pinned version without full teardown).

## 18. What this task explicitly did not do

- No VPS was provisioned, connected to, or configured.
- No script under `deploy/hermes/` was executed.
- No real secret, API key, or credential was created, requested, or stored anywhere in this repository.
- No VPS provider or monthly cost ceiling was selected (`work/BLOCKED.md`).
- Hermes was not installed, activated, or granted any capability. `docs/TOOL_REGISTRY.md`'s Hermes entry remains `status: not integrated`.
- The `ict-trading` profile has no live connection to any trading account, prop-firm platform, or data provider.

## Acceptance

See `docs/14_ACCEPTANCE_TESTS.md` — "Hermes VPS deployment package (HERMES-DEP-001)".
