# Installation runbook

**Not executed by `HERMES-DEP-001`.** This runbook is reviewed and version-controlled ahead of any real VPS. Running it against a real host requires separate, explicit Owner authorization. Commands below are grounded in the official `NousResearch/hermes-agent` Docker deployment (consulted 2026-07-23 against release v0.19.0, 2026-07-20) — see `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` — "Corrections after upstream audit" for what an earlier draft got wrong.

## Preconditions

- Ubuntu LTS VPS provisioned (provider and cost ceiling: `work/BLOCKED.md`, still an open Owner decision).
- Operator has SSH access with a known source CIDR.
- Tailscale (or the selected equivalent tunnel) account/auth key available.
- Docker Engine and Docker Compose plugin installable from the distribution's or Docker's official repository.
- `docs/23_CAPABILITY_MODEL.md`'s KMS/HSM/Vault product selection is either resolved or the interim manual-injection path (`secrets/README.md`) is accepted for this install.

## Steps

1. **Patch the base OS.** `apt update && apt full-upgrade`, reboot if a kernel update applied.
2. **Install Docker Engine + Compose plugin** from the official repository, pinned to a known-good version.
3. **Create the service user.** Copy `deploy/hermes/scripts/create-service-user.sh`, review, run it. Then add it to the `docker` group so it can later run `docker compose exec` for backup/health-check jobs: `usermod -aG docker hermes`. **This grants effectively root-equivalent access via docker.sock** — a real, accepted trade-off (`docs/31_HERMES_DEPLOYMENT_PACKAGE.md` §1, §2), not an oversight.
4. **Bootstrap directories.** Copy `deploy/hermes/scripts/bootstrap-directories.sh`, review, run it.
5. **Install the tunnel client** (Tailscale or equivalent), authenticate, confirm the private-network interface is up. Get its address: `tailscale ip -4`.
6. **Place the Compose project.** Copy `deploy/hermes/core/docker-compose.yml.template` to `/opt/hermes/core/compose/docker-compose.yml` and `deploy/hermes/core/compose.env.example` to `/opt/hermes/core/compose/.env`, then set `TAILSCALE_IP` in that `.env` to the address from step 5. Confirm the image tag in `docker-compose.yml` is pinned to a specific, reviewed version — never `:latest`.
7. **Populate container-level secrets.** Copy `deploy/hermes/secrets/env.template` to `/opt/hermes/core/secrets/.env`, fill in real values directly on the host per `secrets/README.md` (orchestration-level flags only — a dashboard API key, if the dashboard is enabled), then `chmod 0600` and `chown hermes:hermes`.
8. **Firewall.** Review `deploy/hermes/firewall/apply-ufw-rules.sh` and `egress-allowlist.md`. Run it with `SSH_SOURCE_CIDR=<your CIDR> ./apply-ufw-rules.sh` first with no flags (dry run — prints the plan, changes nothing), then add `--apply` during an authorized change window, from a session where you can tolerate the automatic rollback if something is wrong. Do not pass `--apply-egress` unless outbound restriction has been separately decided for this install.
9. **First start (empty state).** As the `hermes` user, from `/opt/hermes/core/compose`: `docker compose up -d`. This creates `/opt/hermes/profiles/ict-trading/state/` contents inside the container for the first time (config.yaml, .env, etc., materialized by Hermes itself on first run).
10. **Materialize the IIOS manifest into Hermes' real config.** `deploy/hermes/profiles/ict-trading.profile.json` is an IIOS-authored manifest, not something Hermes reads directly (`docs/31_HERMES_DEPLOYMENT_PACKAGE.md` §15). After step 9's first run has generated a default `config.yaml` inside the mounted state directory, apply the values from `deploy/hermes/profiles/ict-trading.config.yaml.template` — either by editing `/opt/hermes/profiles/ict-trading/state/config.yaml` directly on the host (the volume is a normal host directory) or via `docker compose exec ict-trading hermes config set <key> <value>` per key. Restart afterward: `docker compose restart ict-trading`.
11. **Populate Hermes' own secrets.** Directly edit `/opt/hermes/profiles/ict-trading/state/.env` (this is `HERMES_HOME/.env`, Hermes' own secrets file — distinct from step 7's container-level file) with the real, read-only data-provider token, per `secrets/README.md`. `chmod 0600`, owned by whatever UID the container's process runs as inside the volume (confirm with `docker compose exec ict-trading id` — not independently confirmed during this design task). **Do not populate an order-capable credential here — this profile is read-only only.**
12. **Install and enable the scheduled jobs.** Copy `deploy/hermes/scripts/run-backup.sh` and `run-healthcheck.sh` to `/opt/hermes/core/compose/scripts/`, `chmod +x`. Copy every file under `deploy/hermes/systemd/` to `/etc/systemd/system/`, `systemctl daemon-reload`, then `systemctl enable --now hermes-backup.timer hermes-healthcheck.timer`.
13. **Verify.** `docker compose ps` shows `ict-trading` running/healthy. `systemctl start hermes-healthcheck.service && journalctl -u hermes-healthcheck.service -n 40` shows an OK entry. `docker compose exec ict-trading hermes doctor` reports clean directly (not just via the scheduled check, as a first-run sanity check).
14. **Record the install** in `work/DONE.md` / `CHANGELOG.md` with the pinned image tag, install date, and host identifier (no credential).

## Post-install state

`ict-trading` is running, health-checked, backed up on schedule, and reachable only over the private tunnel. Its data scope is read-only per `deploy/hermes/profiles/ict-trading.profile.json`, with no standing Governance capability — every action still requires a live Governance Core decision once Hermes is actually integrated into the broader IIOS Governance flow (`ICT-AGENT-001`, `BACKLOG.md`, separately blocked on more than this install).
