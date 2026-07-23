# Backup / restore runbook

**Not executed by `HERMES-DEP-001`.** Reviewed ahead of any real VPS.

## What is backed up

`/opt/hermes/core/compose` (configuration, not secrets) and `/opt/hermes/profiles` (per-profile state). See `scripts/run-backup.sh`.

## What is deliberately excluded

`/opt/hermes/core/secrets/` — the live `.env` file. Reasoning: a backup archive is a second place a secret can leak from, with its own retention and access-control surface to secure. Once a KMS/HSM/Vault product is selected (`work/BLOCKED.md`), secret recovery goes through that product's own backup/recovery mechanism, not this path. Until then, secret recovery after a full loss means re-entering values from their original source (the Owner, or the relevant provider's dashboard) — slower, but it never puts a secret at rest in an unencrypted-by-this-script archive.

## Schedule

`systemd/hermes-backup.timer` — daily, with a randomized delay to avoid predictable-time load spikes.

## Destination

Not selected by this task. `scripts/run-backup.sh` stages a `tar.gz` under `/opt/hermes/backups/` and stops — transport to an external, encrypted destination is left as an explicit extension point once a destination/tool is chosen (`work/BLOCKED.md`), matching `docs/10_INFRASTRUCTURE.md`'s "encrypted volume and external backup" direction. Do not consider backups complete until an external destination exists — a local-only staging copy on the same host provides no protection against host loss.

## Restore

1. Identify the target archive under `/opt/hermes/backups/<timestamp>/hermes-backup.tar.gz` (or its off-host copy).
2. Stop the affected services: `systemctl stop hermes-gateway.service hermes-worker.service`.
3. Move the current (possibly corrupted) `core/compose` and/or `profiles/<name>` directories aside rather than deleting them, until the restore is confirmed good.
4. Extract the archive to `/opt/hermes/`, preserving the paths recorded at backup time.
5. Re-apply ownership/permissions per `directory-layout.md` — extraction can change them.
6. `systemctl start hermes-gateway.service`, then `systemctl start hermes-healthcheck.service` and confirm OK.
7. Only after confirming the restore is healthy: remove the aside-moved directories from step 3.

## Restore testing

A backup that has never been restored is not a verified backup. Before this package is used against a real host, the install runbook's first completed backup cycle should be followed by one deliberate restore-drill on a disposable target, not just trusted on faith — this mirrors the Kill Switch drill cadence already ratified for a different subsystem (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md`) as a general "untested recovery paths are not recovery paths" principle.
