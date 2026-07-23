# Installation runbook

**Not executed by `HERMES-DEP-001`.** This runbook is reviewed and version-controlled ahead of any real VPS. Running it against a real host requires separate, explicit Owner authorization.

## Preconditions

- Ubuntu LTS VPS provisioned (provider and cost ceiling: `work/BLOCKED.md`, still an open Owner decision).
- Operator has SSH access with a known source CIDR.
- Tailscale (or the selected equivalent tunnel) account/auth key available.
- Docker Engine and Docker Compose plugin installable from the distribution's or Docker's official repository.
- `docs/23_CAPABILITY_MODEL.md`'s KMS/HSM/Vault product selection is either resolved or the interim manual-injection path (`secrets/README.md`) is accepted for this install.

## Steps

1. **Patch the base OS.** `apt update && apt full-upgrade`, reboot if a kernel update applied.
2. **Install Docker Engine + Compose plugin** from the official repository, pinned to a known-good version.
3. **Create the service user.** Copy `deploy/hermes/scripts/create-service-user.sh` to the host, review it, run it.
4. **Bootstrap directories.** Copy `deploy/hermes/scripts/bootstrap-directories.sh`, review, run it.
5. **Install the firewall.** Copy `deploy/hermes/firewall/apply-ufw-rules.sh`, set `OPERATOR_SSH_CIDR` (and `TUNNEL_INTERFACE` if not `tailscale0`), review, run it. Verify `ufw status verbose` matches `deploy/hermes/firewall/egress-allowlist.md` before proceeding.
6. **Install the tunnel client** (Tailscale or equivalent), authenticate, confirm the private-network interface is up.
7. **Populate secrets.** Copy `deploy/hermes/secrets/env.template` to `/opt/hermes/core/secrets/.env`, fill in real values directly on the host per `secrets/README.md`, then `chmod 0600` and `chown hermes:hermes`.
8. **Place the Compose stack.** Copy the pinned `docker-compose.yml` (Hermes release artifact, not part of this repository) to `/opt/hermes/core/compose/`, along with `deploy/hermes/scripts/run-backup.sh` and `deploy/hermes/scripts/run-healthcheck.sh` into `/opt/hermes/core/compose/scripts/`.
9. **Install systemd units.** Copy every file under `deploy/hermes/systemd/` to `/etc/systemd/system/`, then `systemctl daemon-reload`.
10. **Enable and start.** `systemctl enable --now hermes-gateway.service`, then `hermes-worker.service` if the worker is used, then `systemctl enable --now hermes-backup.timer hermes-healthcheck.timer`.
11. **Verify.** `systemctl status hermes-gateway.service` shows active; `journalctl -u hermes-healthcheck.service` shows an OK entry within 2 minutes; `docker compose ps` (as the `hermes` user, from `/opt/hermes/core/compose`) shows every service `running`/`healthy`.
12. **Provision the first profile.** `mkdir -p /opt/hermes/profiles/ict-trading/{workspace,state}`, apply ownership/permissions per `directory-layout.md`, place `deploy/hermes/profiles/ict-trading.profile.json` under the profile's config path per the Hermes release's own profile-loading convention. **Do not activate it with a live data-provider token until `ICT-AGENT-001` is separately authorized** (`BACKLOG.md` — `ICT-AGENT-001` is `blocked_by_dependency` on an authorized Hermes installation and approved Governance tests).
13. **Run `hermes doctor`** (`docs/10_INFRASTRUCTURE.md`) and confirm no error.
14. **Record the install** in `work/DONE.md` / `CHANGELOG.md` with the pinned version, install date, and host identifier (no credential).

## Post-install state

Hermes is running, health-checked, backed up on schedule, and reachable only over the private tunnel. The `ict-trading` profile directory exists but has no live capability or credential until a separate task authorizes activation.
