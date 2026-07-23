# Uninstall / rollback runbook

**Not executed by `HERMES-DEP-001`.** Reviewed ahead of any real VPS; running it requires the same authorization as any other real-VPS action.

## Partial rollback (revert to the previous pinned version, no data loss)

Use this path first — it is reversible and does not touch `/opt/hermes/profiles/` or backups.

1. `docker compose stop ict-trading` from `/opt/hermes/core/compose` (if running). There is no gateway-supervising systemd unit to stop — Docker's own `restart: unless-stopped` is the only supervision this package adds (`docs/31_HERMES_DEPLOYMENT_PACKAGE.md` §2).
2. Restore the previous `docker-compose.yml` (the one pinned before the update) to `/opt/hermes/core/compose/`.
3. `docker compose pull` (previous pinned tag) then `docker compose up -d`.
4. Confirm `systemctl start hermes-healthcheck.service && journalctl -u hermes-healthcheck.service` returns to OK within 5 minutes.
5. If still failing, proceed to full uninstall + reinstall from the last known-good backup (`BACKUP_RESTORE.md`).

This mirrors `docs/10_INFRASTRUCTURE.md`'s upgrade policy's "rollback readiness" step — it is the same procedure `UPDATE_ROLLBACK.md` references, listed here in full because uninstall/rollback is its own `HERMES-DEP-001` deliverable.

## Full uninstall (destructive — confirm intent before running)

1. `systemctl disable --now hermes-backup.timer hermes-healthcheck.timer` (the only systemd units this package installs — no gateway/worker unit exists).
2. `docker compose down --volumes` from `/opt/hermes/core/compose` (removes containers, networks, and named volumes — **not** bind-mounted host data under `/opt/hermes/profiles/`, which is untouched by this command).
3. Remove the systemd unit files from `/etc/systemd/system/`, `systemctl daemon-reload`.
4. Revoke the firewall's tunnel/egress rules: `ufw --force reset` if the host is being fully decommissioned, or leave them if the host continues to serve another purpose.
5. **Confirm a final backup exists and has been restore-tested** (`BACKUP_RESTORE.md`) before removing `/opt/hermes/` itself.
6. Only after the above: `rm -rf /opt/hermes` and `userdel hermes` if the host is being fully decommissioned.
7. Record the uninstall in `work/DONE.md` / `CHANGELOG.md` with the reason and the backup reference retained.

## Rule

Step 5 is not optional. No uninstall proceeds to host data removal without a verified, restorable backup already confirmed off-host.
