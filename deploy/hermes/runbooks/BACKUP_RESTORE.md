# Backup / restore runbook

**Not executed by `HERMES-DEP-001`.** Reviewed ahead of any real VPS.

## What is backed up

`deploy/hermes/scripts/run-backup.sh` runs the **official** `hermes backup` command inside the running container via `docker compose exec` (confirmed against `NousResearch/hermes-agent`'s CLI reference, consulted 2026-07-23 against release v0.19.0) — not a raw `tar` of arbitrary host paths. `hermes backup` itself decides what belongs in a coherent backup (config, skills, sessions, data) and excludes the agent codebase, so this cannot sweep up a cache or virtualenv the way a naive tar of the whole state directory could.

## What is deliberately excluded

- `/opt/hermes/core/secrets/.env` — the container/orchestration-level secrets file. A backup archive is a second place a secret can leak from, with its own retention and access-control surface to secure.
- Whatever `hermes backup` itself excludes upstream (the agent codebase) — not independently re-verified item-by-item during this design task; treat the official command's own exclusions as authoritative rather than re-implementing a parallel exclusion list.

Once a KMS/HSM/Vault product is selected (`work/BLOCKED.md`), secret recovery goes through that product's own mechanism, not this path. Until then, secret recovery after a full loss means re-entering values from their original source (the Owner, or the relevant provider's dashboard).

## Schedule

`systemd/hermes-backup.timer` — daily, with a randomized delay to avoid predictable-time load spikes.

## Destination

Not selected by this task. `run-backup.sh` moves the archive `hermes backup -o ...` produces to `/opt/hermes/backups/` and stops — transport to an external, encrypted destination is left as an explicit extension point once a destination/tool is chosen (`work/BLOCKED.md`), matching `docs/10_INFRASTRUCTURE.md`'s "encrypted volume and external backup" direction. Do not consider backups complete until an external destination exists — a local-only staging copy on the same host provides no protection against host loss.

## Restore

Uses the official `hermes import <zipfile>` command (CLI reference), not a raw archive extraction over the state directory:

1. Identify the target archive under `/opt/hermes/backups/hermes-backup-<timestamp>.zip` (or its off-host copy).
2. `docker compose stop ict-trading` from `/opt/hermes/core/compose`. There is no gateway-supervising systemd unit to stop — Docker's own `restart: unless-stopped` is the only supervision this package adds.
3. Move the current (possibly corrupted) `profiles/ict-trading/state` directory aside rather than deleting it, until the restore is confirmed good, then recreate an empty `state/` in its place.
4. `docker compose up -d ict-trading` to get a fresh container instance running against the empty state directory, then `docker compose exec ict-trading hermes import /opt/data/backups/<archive-name>.zip` (copy the archive into the mounted volume first if restoring from an off-host copy).
5. Re-apply ownership/permissions per `directory-layout.md` if needed — restore can change them.
6. `systemctl start hermes-healthcheck.service` and confirm OK; separately run `docker compose exec ict-trading hermes doctor` as a direct sanity check.
7. Only after confirming the restore is healthy: remove the aside-moved directory from step 3.

The exact `hermes import` flag/argument shape was not independently exercised against a running instance during this design task — confirm against `hermes import --help` (or the CLI reference) on the actual pinned version before relying on this in a real incident.

## Restore testing

A backup that has never been restored is not a verified backup. Before this package is used against a real host, the install runbook's first completed backup cycle should be followed by one deliberate restore-drill on a disposable target, not just trusted on faith — this mirrors the Kill Switch drill cadence already ratified for a different subsystem (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md`) as a general "untested recovery paths are not recovery paths" principle.
