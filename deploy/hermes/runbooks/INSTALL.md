# Installation runbook

**Not executed by this design/preparation task.** Reviewed and version-controlled ahead of any real VPS. Running it requires `HERMES-INSTALL-001` to be separately authorized (`BACKLOG.md`) — a real VPS, purchased and Owner-authorized, non-secret VPS metadata supplied by the Owner, and confirmed SSH public-key access. Grounded in the official `NousResearch/hermes-agent` Docker deployment (consulted 2026-07-23 against release v0.19.0, tag `v2026.7.20`, commit `3ef6bbd201263d354fd83ec55b3c306ded2eb72a`) — see `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` for the full correction history, including the reversal from an earlier one-container-per-profile design to the single-container, multi-profile topology used below.

## Preconditions

- Ubuntu LTS VPS provisioned and Owner-authorized (provider and cost ceiling: `work/BLOCKED.md`, resolved by `HERMES-INSTALL-001`'s own gating).
- Operator has SSH access with a known source CIDR and confirmed public-key auth.
- Tailscale (or the selected equivalent tunnel) account/auth key available.
- Docker Engine and Docker Compose plugin installable from the distribution's or Docker's official repository.
- `docs/23_CAPABILITY_MODEL.md`'s KMS/HSM/Vault product selection is either resolved or the interim manual-injection path (`secrets/README.md`) is accepted for this install.
- The VPS's CPU architecture is confirmed (linux/amd64 assumed by `core/docker-compose.yml.template`'s pinned digest — swap in the linux/arm64 digest from `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` if it's ARM).

## Steps

1. **Patch the base OS.** `apt update && apt full-upgrade`, reboot if a kernel update applied.
2. **Install Docker Engine + Compose plugin** from the official repository, pinned to a known-good version.
3. **Create the service user.** Copy `deploy/hermes/scripts/create-service-user.sh`, review, run it. Then add it to the `docker` group so it can later run `docker exec`/`docker inspect`/`docker logs` for the health check: `usermod -aG docker hermes`. **This grants effectively root-equivalent access via docker.sock** — a real, accepted trade-off (`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`), not an oversight. Backups no longer need this (host-level tar, see `BACKUP_RESTORE.md`).
4. **Bootstrap directories.** Copy `deploy/hermes/scripts/bootstrap-directories.sh`, review, run it. This creates the single shared `/opt/hermes/data` volume directory — do not create per-profile subdirectories manually.
5. **Install the tunnel client** (Tailscale or equivalent), authenticate, confirm the private-network interface is up. Get its address: `tailscale ip -4`.
6. **Place the Compose project.** Copy `deploy/hermes/core/docker-compose.yml.template` to `/opt/hermes/core/compose/docker-compose.yml` and `deploy/hermes/core/compose.env.example` to `/opt/hermes/core/compose/.env`, then set `TAILSCALE_IP` in that `.env` to the address from step 5. Confirm the image reference is still the pinned digest recorded in `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` — never switch to a tag or `:latest`.
7. **Populate container-level secrets.** Copy `deploy/hermes/secrets/env.template` to `/opt/hermes/core/secrets/.env`, fill in real values directly on the host per `secrets/README.md` (orchestration-level flags only — a dashboard API key, if the dashboard is ever enabled), then `chmod 0600` and `chown hermes:hermes`.
8. **Firewall.** Review `deploy/hermes/firewall/apply-ufw-rules.sh` and `egress-allowlist.md`. Run with `SSH_SOURCE_CIDR=<your CIDR> ./apply-ufw-rules.sh` first with no flags (dry run — prints the plan, changes nothing), then add `--apply` during an authorized change window, from a session where you can tolerate the automatic rollback if something is wrong. Do not pass `--apply-egress` unless outbound restriction has been separately decided for this install.
9. **First start (empty volume).** As the `hermes` user, from `/opt/hermes/core/compose`: `docker compose up -d`. The container's entrypoint seeds a default `config.yaml`/`.env`/`SOUL.md` into `/opt/hermes/data` on first boot — no interactive setup wizard is required for a profile with no API key yet (`onyx` v0.1 needs none).
10. **Verify the container itself.** `docker compose ps` shows `hermes` running/healthy (the compose `healthcheck:` block uses `hermes status`). `docker exec hermes hermes doctor` reports clean.
11. **Create the `onyx` profile.** `docker exec hermes hermes profile create onyx` — registers its s6-supervised gateway slot at `/run/service/gateway-onyx/` and its own subtree at `/opt/hermes/data/profiles/onyx/`. **Do not start its gateway or populate any credential** — `onyx` remains `specified`, `not_activated` (`deploy/hermes/profiles/onyx/onyx.profile.json`) until a separate Owner authorization activates it (`BACKLOG.md` `ONYX-CORE-001`, which itself depends on this install being completed and health-checked). Confirm the profile's actual `HERMES_HOME` resolution for `terminal.home_mode: profile` against `docker exec hermes hermes config show -p onyx` before relying on the `terminal.cwd` value already recorded in the manifest — that value was not independently confirmed during the design task and is flagged there as such.
12. **Install and enable the scheduled jobs.** Copy `deploy/hermes/scripts/run-backup.sh` and `run-healthcheck.sh` to `/opt/hermes/core/compose/scripts/`, `chmod +x`. Copy every file under `deploy/hermes/systemd/` to `/etc/systemd/system/`, `systemctl daemon-reload`, then `systemctl enable --now hermes-backup.timer hermes-healthcheck.timer`.
13. **Verify the scheduled jobs.** `systemctl start hermes-backup.service` and confirm an archive appears in `/opt/hermes/backups/`. `systemctl start hermes-healthcheck.service && journalctl -u hermes-healthcheck.service -n 60` shows an OK entry, including an `OK: profile 'onyx' gateway status reported healthy` line (or an `INFO: no profiles created yet` line if step 11 was skipped).
14. **Record the install** in `work/DONE.md` / `CHANGELOG.md` with the pinned image digest, install date, and host identifier (no credential).

## Post-install state

The single Hermes container is running, health-checked, backed up on schedule, and reachable only over the private tunnel (no port published unless a real profile needs one). `onyx` exists as a created-but-not-started profile with no credential and no standing capability. No other profile exists yet. This is the completion state `ONYX-CORE-001` depends on before its own activation work can begin — activation itself is a separate, future authorization.
