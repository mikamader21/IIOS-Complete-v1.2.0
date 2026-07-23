# Backup / restore runbook

**Not executed by this design/preparation task.** Reviewed ahead of any real VPS.

## What is backed up

`deploy/hermes/scripts/run-backup.sh` runs a plain host-level `tar` of `/opt/hermes/data` — the **single** shared Hermes `HERMES_HOME`, covering every co-located profile in one archive. This changed from the earlier per-profile-container design's use of the official `hermes backup` CLI command: that command's exclusion of the agent codebase is no longer needed to keep the archive clean, because in the Docker deployment the codebase (venv, node_modules, Playwright) lives entirely inside the immutable image at `/opt/hermes`, never on the bind-mounted `/opt/hermes/data` volume — so a plain tar of the volume structurally cannot sweep up a cache or venv, the same guarantee the CLI command existed to provide.

## What this means for secrets

Unlike the earlier design, this archive **does** include Hermes' own `.env` files (root and per-profile) once any profile is actually activated with real credentials — that is by design, matching upstream's own backup/restore semantics (`.env` is explicitly part of what `hermes backup`/`hermes import` cover). As of this design task nothing is activated, so no real secret exists in any archive produced right now. **From the first real profile activation onward, treat every backup archive as containing live secrets** — encrypt it at rest and restrict access accordingly. This is a genuine change in posture from the earlier per-profile design's "no secret in backup" claim, made explicit rather than carried over silently.

Deliberately still excluded: `/opt/hermes/core/secrets/.env` — the container/orchestration-level file (e.g. a dashboard API key), which is not part of Hermes' own state and is backed up, if at all, through whatever mechanism secures the rest of the host's `/opt/hermes/core/` configuration.

## Schedule

`systemd/hermes-backup.timer` — daily, with a randomized delay to avoid predictable-time load spikes.

## Destination

Not selected by this task. `run-backup.sh` stages a `tar.gz` under `/opt/hermes/backups/` and stops — transport to an external, encrypted destination is left as an explicit extension point once a destination/tool is chosen (`work/BLOCKED.md`), matching `docs/10_INFRASTRUCTURE.md`'s "encrypted volume and external backup" direction. Do not consider backups complete until an external destination exists — a local-only staging copy on the same host provides no protection against host loss.

## Restore

1. Identify the target archive under `/opt/hermes/backups/hermes-data-<timestamp>.tar.gz` (or its off-host copy).
2. `docker compose stop hermes` from `/opt/hermes/core/compose`. There is no gateway-supervising systemd unit to stop — Docker's own `restart: unless-stopped` plus the image's built-in s6-overlay are the only supervision this package adds.
3. Move the current (possibly corrupted) `/opt/hermes/data` directory aside rather than deleting it, until the restore is confirmed good.
4. Extract the archive to `/opt/hermes/`, so it recreates `/opt/hermes/data/` in place.
5. Re-apply ownership/permissions per `directory-layout.md` if needed — extraction can change them (`chown -R hermes:hermes /opt/hermes/data && chmod 0750 /opt/hermes/data`).
6. `docker compose up -d`, then `systemctl start hermes-healthcheck.service` and confirm OK, including an OK line for every profile that existed at backup time. Separately run `docker exec hermes hermes doctor` as a direct sanity check.
7. Only after confirming the restore is healthy: remove the aside-moved directory from step 3.

Because the restore now brings back **every** co-located profile at once (there is no per-profile restore), a single corrupted profile cannot be restored in isolation without restoring the whole shared volume — a real, accepted consequence of the one-container/one-volume topology, not previously true under the earlier per-profile-directory design.

## Restore testing

A backup that has never been restored is not a verified backup. Before this package is used against a real host, the install runbook's first completed backup cycle should be followed by one deliberate restore-drill on a disposable target, not just trusted on faith — this mirrors the Kill Switch drill cadence already ratified for a different subsystem (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md`) as a general "untested recovery paths are not recovery paths" principle.
