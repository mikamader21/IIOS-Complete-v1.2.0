# Update / rollback runbook

**Not executed by this design/preparation task.** Implements `docs/10_INFRASTRUCTURE.md`'s upgrade policy for the Hermes deployment specifically; does not redefine it. "Pinned" now means pinned by image digest (`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`), not tag alone — an update always changes the digest.

## Update

1. **Release watch.** Per `docs/17_WEEKLY_WATCH.md`'s cadence, check `github.com/NousResearch/hermes-agent/releases` for a new tag, and Docker Hub for the matching image digest — the same two-source cross-check used to resolve the pin recorded in `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`. Never trust a single source for the digest.
2. **Read notes/security.** Confirm no unreviewed breaking change or CVE in the dependency chain. Check specifically for any change to the multi-profile/s6-supervision behavior this deployment relies on.
3. **Staging backup.** Run `hermes-backup.service` manually (`systemctl start hermes-backup.service`) and confirm the resulting archive is present in `/opt/hermes/backups/` before touching anything else. Because every profile shares one volume, this single backup covers all of them — there is no per-profile granularity to fall back on.
4. **Pinned upgrade.** Update the `image:` digest in `/opt/hermes/core/compose/docker-compose.yml` to the new, independently-verified digest — never a tag alone, never `:latest`.
5. **Tests.** `docker compose pull`, `docker compose up -d`, then `systemctl start hermes-healthcheck.service` and confirm OK, including an OK line for every profile that existed before the update. Also run `docker exec hermes hermes doctor` directly as a first-run sanity check, not only via the scheduled health check. The container's entrypoint runs non-interactive config-schema migrations against the mounted `config.yaml` on this start — it writes timestamped backups of `config.yaml`/`.env` next to the originals first (upstream behavior); confirm those backup files appear.
6. **Observation window.** Monitor `docker logs -f hermes` and `journalctl -u hermes-healthcheck.service` for a period appropriate to the change's risk (a patch release warrants less observation than a major version). There is no gateway-supervising systemd unit to watch — `docker compose ps` / `docker inspect`'s health status is the source of truth for whether the update is running.
7. **Production approval.** Owner confirms the observation window is clean before the update is considered final.
8. **Rollback readiness.** The previous pinned digest is kept in a comment or a `docker-compose.yml.previous` copy until the observation window closes, so `UNINSTALL_ROLLBACK.md`'s partial-rollback path is a two-command operation, not a reconstruction.

## Rollback

See `UNINSTALL_ROLLBACK.md` — "Partial rollback." That section is this runbook's rollback path; it is not duplicated here to avoid the two documents drifting apart.

## Rule

No update step 4 (pinned upgrade) proceeds without a confirmed staging backup from step 3, and without the new digest independently verified against at least two official sources (matching how the digest recorded in `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` was itself verified — GitHub release/tag plus Docker Hub, not one alone). No update is "final" without an explicit Owner production approval (step 7).
