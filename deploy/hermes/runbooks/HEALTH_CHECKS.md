# Health checks runbook

**Not executed by `HERMES-DEP-001`.** Reviewed ahead of any real VPS.

## What is checked

`deploy/hermes/scripts/run-healthcheck.sh` checks, in order: the `ict-trading` container's running state (`docker compose ps`), a restart-count heuristic via `docker inspect` (possible restart loop — compared against the previous run, stored in `/opt/hermes/logs/healthcheck-restart-count.state`), host disk free (`/opt/hermes`) and available memory, the **official** `hermes doctor` command (config/dependency diagnosis) and `hermes gateway status` (both run inside the container via `docker compose exec`, confirmed against `NousResearch/hermes-agent`'s CLI reference, consulted 2026-07-23 against release v0.19.0), `HERMES_HOME` writability, and the last 20 lines of `docker compose logs` for the profile.

## What is not checked

This is a liveness/diagnostic check, not a correctness check — `hermes doctor` catches config/dependency issues, not whether Hermes is behaving correctly against Governance or whether any profile's data is accurate. Egress-reachability-to-allowed-providers is explicitly **skipped**, not faked — no model/data provider has been selected yet (`work/BLOCKED.md`), so there is no real hostname to check without guessing one; add a concrete check once a provider exists.

## Schedule

`systemd/hermes-healthcheck.timer` — 2 minutes after boot, then every 5 minutes.

## On failure

`run-healthcheck.sh` exits non-zero and prints `FAIL: ...` lines (captured by the journal via systemd). The health-check unit **does not restart anything** — it only observes and logs. Recovery is Docker's own `restart: unless-stopped` policy on the container; there is no gateway-supervising systemd unit in this package (`docs/31_HERMES_DEPLOYMENT_PACKAGE.md` §2) to exhaust a restart-burst limit on. If Docker's own restart policy has been cycling repeatedly, the script's restart-count heuristic (§ "What is checked") is what surfaces that, not a systemd-level signal.

## Alerting

Not implemented by this package — `journalctl -u hermes-healthcheck.service` is the source of truth until an alerting integration is separately authorized. Do not assume a silent failure is impossible; check the journal, or wire an alert, before relying on this check for unattended operation.

## Secrets in check output

`hermes doctor` and `hermes gateway status` output is always redirected to `/tmp/hermes-doctor.out` / `/tmp/hermes-gateway-status.out`, not printed to the journal, and only surfaced by the script (as a "see /tmp/..." pointer) when the command fails. Treat those files as internal-only and clean them up after review — this design task did not independently verify that neither command ever surfaces a secret value in its output; do not ship those files anywhere outside the host without checking first.

## Verifying the check itself works

After install, deliberately stop the container (`docker compose stop ict-trading`) and confirm the next health-check run within 5 minutes reports `FAIL: hermes-ict-trading is not in a running state`. Restart it (`docker compose start ict-trading`) and confirm the following run reports OK. This is a one-time verification during install, not a standing test.
