# Hermes VPS Deployment Package

Design/preparation artifacts for `HERMES-DEP-001` (`BACKLOG.md`) and its topology reconciliation ahead of `HERMES-INSTALL-001`. See `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` for the full write-up and `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` (**Ratified**) for the architecture decision these files implement.

**Nothing in this directory has been executed against a real host.** Every script is a reviewed template; every config is a template with placeholder values. Connecting to or modifying a real VPS requires `HERMES-INSTALL-001`'s own separate authorization (`work/BLOCKED.md`, `BACKLOG.md`).

This package was twice checked against the real, official `NousResearch/hermes-agent` product — first an initial pre-merge audit (release v0.19.0, corrections recorded in `docs/31`), then a second, deeper reconciliation (release/digest re-verification plus a topology correction from one-container-per-profile to **one container hosting multiple s6-supervised profiles**, matching the product's own current recommended pattern). Both rounds are recorded in `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` and in each affected file's own comments.

## Layout

```text
deploy/hermes/
  README.md                      — this file
  directory-layout.md            — target /opt/hermes/ tree (single shared data/ volume)
  scripts/
    create-service-user.sh       — creates the unprivileged `hermes` host OS user
    bootstrap-directories.sh     — creates /opt/hermes/* with correct ownership/permissions
    run-backup.sh                — host-level tar of the shared /opt/hermes/data volume
    run-healthcheck.sh           — docker exec's `hermes doctor` + per-profile `gateway status`
                                    (loops over whatever profiles exist) + host checks
  core/
    docker-compose.yml.template  — ONE official Hermes container, pinned by image digest
                                    (verified against GitHub + Docker Hub, 2026-07-23),
                                    hosting every profile — no per-profile service, no
                                    "worker" service (there is no such thing upstream)
    compose.env.example          — Docker Compose's own project .env (TAILSCALE_IP) —
                                    distinct from the two secrets files below
  systemd/
    hermes-backup.service        — one-shot backup job (host-level tar, no docker exec)
    hermes-backup.timer          — schedules the backup job
    hermes-healthcheck.service   — one-shot liveness check (docker exec, needs `docker` group)
    hermes-healthcheck.timer     — schedules the health check
    (no gateway/worker unit — Docker's own `restart: unless-stopped` plus the image's own
    built-in s6-overlay supervise the container and each profile's gateway; a custom
    systemd wrapper would duplicate that, not the official `hermes gateway install
    --system` mechanism, which is for the native, non-Docker install path this package
    does not use)
  firewall/
    apply-ufw-rules.sh           — dry-run by default; --apply required, --apply-egress
                                    separately required for outbound rules; rollback safety net
    egress-allowlist.md          — destinations table and rationale
  secrets/
    env.template                 — container/orchestration-level flags only, placeholder values
    README.md                    — the three-file secret-injection design, no real secrets
  profiles/
    ict-trading.profile.json           — IIOS deployment manifest for a FUTURE named
                                          profile inside the shared container (not
                                          activated by any task so far)
    ict-trading.config.yaml.template   — the real Hermes config.yaml fragment this maps to
    onyx/
      onyx.profile.json                — Executive Orchestrator manifest (docs/32) — the
                                          FIRST profile, specification only, not activated
  runbooks/
    INSTALL.md
    UNINSTALL_ROLLBACK.md
    UPDATE_ROLLBACK.md
    BACKUP_RESTORE.md
    HEALTH_CHECKS.md
```

## Isolation model, stated plainly

Every profile above shares one container, one kernel namespace, one container-internal OS user. Separation between co-located profiles is **application-layer only** (separate `HERMES_HOME` subtree, separate credentials, separate s6 gateway slot) — not an OS or container boundary. See `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` — "Real isolation boundaries" for the full breakdown, and "Future dedicated-container option" for the documented (not yet exercised) escape hatch for a profile whose risk profile doesn't fit that boundary.
