# Hermes VPS Deployment Package

Design/preparation artifacts for `HERMES-DEP-001` (`BACKLOG.md`). See `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` for the full write-up and `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` for the architecture decision these files implement.

**Nothing in this directory has been executed against a real host.** Every script is a reviewed template; every config is a template with placeholder values. Connecting to or modifying a real VPS requires separate, explicit Owner authorization (`work/BLOCKED.md`).

This package was audited against the real, official `NousResearch/hermes-agent` product (release v0.19.0, 2026-07-20; docs/CLI reference consulted 2026-07-23) after an initial draft invented commands and config keys that do not exist upstream. That audit's corrections are recorded in `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` — "Corrections after upstream audit" and in each affected file's own comments.

## Layout

```text
deploy/hermes/
  README.md                      — this file
  directory-layout.md            — target /opt/hermes/ tree
  scripts/
    create-service-user.sh       — creates the unprivileged `hermes` OS user
    bootstrap-directories.sh     — creates /opt/hermes/* with correct ownership/permissions
    run-backup.sh                — docker compose exec's the official `hermes backup`
    run-healthcheck.sh           — docker compose exec's `hermes doctor`/`gateway status` + host checks
  core/
    docker-compose.yml.template  — official single-container deployment, pinned tag, one
                                    service per IIOS profile (no "worker" service — see
                                    docs/31, there is no such thing upstream)
    compose.env.example          — Docker Compose's own project .env (TAILSCALE_IP) —
                                    distinct from the two secrets files below
  systemd/
    hermes-backup.service        — one-shot backup job (docker compose exec)
    hermes-backup.timer          — schedules the backup job
    hermes-healthcheck.service   — one-shot liveness check (docker compose exec)
    hermes-healthcheck.timer     — schedules the health check
    (no gateway/worker unit — Docker's own `restart: unless-stopped` supervises the
    container; a custom systemd wrapper would duplicate that, not the official
    `hermes gateway install --system` mechanism, which is for the native, non-Docker
    install path this package does not use)
  firewall/
    apply-ufw-rules.sh           — dry-run by default; --apply required, --apply-egress
                                    separately required for outbound rules; rollback safety net
    egress-allowlist.md          — destinations table and rationale
  secrets/
    env.template                 — container/orchestration-level flags only, placeholder values
    README.md                    — the three-file secret-injection design, no real secrets
  profiles/
    ict-trading.profile.json           — IIOS deployment manifest (not native Hermes config)
    ict-trading.config.yaml.template   — the real Hermes config.yaml fragment this maps to
    onyx/
      onyx.profile.json                — Executive Orchestrator manifest (docs/32),
                                          specification only — no config.yaml counterpart,
                                          no materializer, different path root (flagged)
  runbooks/
    INSTALL.md
    UNINSTALL_ROLLBACK.md
    UPDATE_ROLLBACK.md
    BACKUP_RESTORE.md
    HEALTH_CHECKS.md
```
