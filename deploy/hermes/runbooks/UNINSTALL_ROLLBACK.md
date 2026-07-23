# Uninstall / rollback runbook

**Not executed by this design/preparation task.** Reviewed ahead of any real VPS; running it requires the same authorization as any other real-VPS action.

## Partial rollback (revert to the previous pinned image, no data loss)

Use this path first — it is reversible and does not touch `/opt/hermes/data` or backups. Because the topology is now one shared container/volume for every profile, this rollback affects **every** co-located profile at once — there is no per-profile rollback.

1. `docker compose stop hermes` from `/opt/hermes/core/compose` (if running).
2. Restore the previous pinned `image:` reference (the digest recorded before the update) to `docker-compose.yml`.
3. `docker compose pull` (previous pinned digest) then `docker compose up -d`.
4. Confirm `systemctl start hermes-healthcheck.service && journalctl -u hermes-healthcheck.service` returns to OK within 5 minutes, including an OK line for every profile that existed before the update.
5. If still failing, proceed to full uninstall + reinstall from the last known-good backup (`BACKUP_RESTORE.md`).

This mirrors `docs/10_INFRASTRUCTURE.md`'s upgrade policy's "rollback readiness" step — it is the same procedure `UPDATE_ROLLBACK.md` references, listed here in full because uninstall/rollback is its own deliverable.

## Full uninstall (destructive — confirm intent before running)

1. `systemctl disable --now hermes-backup.timer hermes-healthcheck.timer` (the only systemd units this package installs — no gateway/worker unit exists; Docker's `restart: unless-stopped` plus the image's own s6-overlay supervise the container itself).
2. `docker compose down --volumes` from `/opt/hermes/core/compose` (removes the container and any named/anonymous volumes — **not** the bind-mounted `/opt/hermes/data`, which is untouched by this command since it is a host bind mount, not a Docker-managed volume).
3. Remove the systemd unit files from `/etc/systemd/system/`, `systemctl daemon-reload`.
4. Revoke the firewall's tunnel/egress rules: `ufw --force reset` if the host is being fully decommissioned, or leave them if the host continues to serve another purpose.
5. **Confirm a final backup exists and has been restore-tested** (`BACKUP_RESTORE.md`) before removing `/opt/hermes/data` — this single directory now holds state for every co-located profile, not just one, so its loss is total, not partial.
6. Only after the above: `rm -rf /opt/hermes` and `userdel hermes` if the host is being fully decommissioned.
7. Record the uninstall in `work/DONE.md` / `CHANGELOG.md` with the reason and the backup reference retained.

## Rule

Step 5 is not optional. No uninstall proceeds to host data removal without a verified, restorable backup already confirmed off-host — and because every profile now shares one volume, that single backup's integrity matters more than it did under the earlier per-profile-directory design.
