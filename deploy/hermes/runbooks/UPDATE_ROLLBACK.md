# Update / rollback runbook

**Not executed by `HERMES-DEP-001`.** Implements `docs/10_INFRASTRUCTURE.md`'s upgrade policy for the Hermes deployment specifically; does not redefine it.

## Update

1. **Release watch.** Per `docs/17_WEEKLY_WATCH.md`'s cadence, note the new Hermes release and its changelog.
2. **Read notes/security.** Confirm no unreviewed breaking change or CVE in the dependency chain.
3. **Staging backup.** Run `hermes-backup.service` manually (`systemctl start hermes-backup.service`) and confirm the resulting archive is present in `/opt/hermes/backups/` before touching anything else.
4. **Pinned upgrade.** Update the image tag(s) in `/opt/hermes/core/compose/docker-compose.yml` to the new pinned version — never `:latest`.
5. **Tests.** `docker compose pull`, `docker compose up -d`, then `systemctl start hermes-healthcheck.service` and confirm OK. Also run `docker compose exec ict-trading hermes doctor` directly as a first-run sanity check, not only via the scheduled health check.
6. **Observation window.** Monitor `docker compose logs -f ict-trading` and `journalctl -u hermes-healthcheck.service` for a period appropriate to the change's risk (a patch release warrants less observation than a major version). There is no gateway-supervising systemd unit to watch — Docker's own container state (`docker compose ps`) is the source of truth for whether the update is running.
7. **Production approval.** Owner confirms the observation window is clean before the update is considered final.
8. **Rollback readiness.** The previous pinned `docker-compose.yml` is kept (e.g. `docker-compose.yml.previous`) until the observation window closes, so `UNINSTALL_ROLLBACK.md`'s partial-rollback path is a two-command operation, not a reconstruction.

## Rollback

See `UNINSTALL_ROLLBACK.md` — "Partial rollback." That section is this runbook's rollback path; it is not duplicated here to avoid the two documents drifting apart.

## Rule

No update step 4 (pinned upgrade) proceeds without a confirmed staging backup from step 3. No update is "final" without an explicit Owner production approval (step 7).
