# Hermes VPS Deployment Package

Design/preparation artifacts for `HERMES-DEP-001` (`BACKLOG.md`). See `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` for the full write-up and `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` for the architecture decision these files implement.

**Nothing in this directory has been executed against a real host.** Every script is a reviewed template; every config is a template with placeholder values. Connecting to or modifying a real VPS requires separate, explicit Owner authorization (`work/BLOCKED.md`).

## Layout

```text
deploy/hermes/
  README.md                      — this file
  directory-layout.md            — target /opt/hermes/ tree
  scripts/
    create-service-user.sh       — creates the unprivileged `hermes` OS user
    bootstrap-directories.sh     — creates /opt/hermes/* with correct ownership/permissions
  systemd/
    hermes-gateway.service       — supervises the Hermes Docker Compose stack
    hermes-worker.service        — supervises the Hermes worker Compose service
    hermes-backup.service        — one-shot backup job
    hermes-backup.timer          — schedules the backup job
    hermes-healthcheck.service   — one-shot liveness check
    hermes-healthcheck.timer     — schedules the health check
  firewall/
    apply-ufw-rules.sh           — default-deny inbound/outbound + explicit allowlist
    egress-allowlist.md          — destinations table and rationale
  secrets/
    env.template                 — every expected environment variable, placeholder values only
    README.md                    — injection design, no real secrets
  profiles/
    ict-trading.profile.json     — first Hermes profile: read-only, no order endpoint
  runbooks/
    INSTALL.md
    UNINSTALL_ROLLBACK.md
    UPDATE_ROLLBACK.md
    BACKUP_RESTORE.md
    HEALTH_CHECKS.md
```
