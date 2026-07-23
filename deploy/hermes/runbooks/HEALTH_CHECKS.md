# Health checks runbook

**Not executed by this design/preparation task.** Reviewed ahead of any real VPS.

## Two layers, not a duplicate

1. **Docker's own `healthcheck:` block** (`core/docker-compose.yml.template`) runs `hermes status` inside the container on a short interval — this feeds `docker compose ps`/`docker inspect`'s health status directly and is Docker-native, always on.
2. **`deploy/hermes/scripts/run-healthcheck.sh`**, scheduled by `systemd/hermes-healthcheck.timer`, is a deeper, host-level check: container running state, a restart-count heuristic (possible restart loop), host disk/memory, `hermes doctor`, and — looping over every profile the container currently hosts via `hermes profile list` — a per-profile `hermes -p <name> gateway status`.

These do not conflict: Docker's healthcheck only *reports* status (it doesn't restart or supervise anything itself, matching the "one restart supervisor" rule in `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`), while the external script is a separate observability pass with checks Docker's healthcheck can't express (host resources, per-profile detail).

## What is checked

See `run-healthcheck.sh` — grounded in the **official** `hermes doctor`, `hermes profile list`, and `hermes -p <name> gateway status` commands (confirmed against `NousResearch/hermes-agent`'s CLI reference, consulted 2026-07-23 against release v0.19.0 / tag `v2026.7.20`), run inside the container via `docker exec`.

## What is not checked

This is a liveness/diagnostic check, not a correctness check — `hermes doctor` catches config/dependency issues, not whether Hermes is behaving correctly against Governance or whether any profile's data is accurate. Egress-reachability-to-allowed-providers is explicitly **skipped**, not faked — no model/data provider has been selected yet (`work/BLOCKED.md`), so there is no real hostname to check without guessing one; add a concrete check once a provider exists.

## Schedule

`systemd/hermes-healthcheck.timer` — 2 minutes after boot, then every 5 minutes.

## On failure

`run-healthcheck.sh` exits non-zero and prints `FAIL: ...` lines (captured by the journal via systemd). The health-check unit **does not restart anything** — it only observes and logs. Recovery is Docker's own `restart: unless-stopped` policy on the container plus the image's own built-in s6-overlay auto-restarting a crashed profile gateway; there is no gateway-supervising systemd unit in this package for either to conflict with.

## Alerting

Not implemented by this package — `journalctl -u hermes-healthcheck.service` is the source of truth until an alerting integration is separately authorized. Do not assume a silent failure is impossible; check the journal, or wire an alert, before relying on this check for unattended operation.

## Secrets in check output

`hermes doctor` and per-profile `gateway status` output is always redirected to `/tmp/hermes-doctor.out` / `/tmp/hermes-gateway-status-<profile>.out`, not printed to the journal, and only surfaced by the script (as a "see /tmp/..." pointer) when the command fails. Treat those files as internal-only and clean them up after review — this design task did not independently verify that neither command ever surfaces a secret value in its output; do not ship those files anywhere outside the host without checking first.

## Verifying the check itself works

After install, deliberately stop the container (`docker compose stop hermes`) and confirm the next health-check run within 5 minutes reports `FAIL: hermes is not running`. Restart it (`docker compose start hermes`) and confirm the following run reports OK, including a per-profile OK line for every profile that exists. This is a one-time verification during install, not a standing test.
