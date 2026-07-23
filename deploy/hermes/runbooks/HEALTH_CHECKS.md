# Health checks runbook

**Not executed by `HERMES-DEP-001`.** Reviewed ahead of any real VPS.

## What is checked

`scripts/run-healthcheck.sh` inspects `docker compose ps` output for every service in the Hermes Compose stack and fails if any service is not `running`/`healthy`.

## What is not checked

This is a liveness check, not a correctness check — it confirms processes are up, not that Hermes is behaving correctly against Governance, or that any profile's data is accurate. Deeper functional checks are a future extension, not part of this deliverable.

## Schedule

`systemd/hermes-healthcheck.timer` — 2 minutes after boot, then every 5 minutes.

## On failure

`run-healthcheck.sh` exits non-zero and logs `UNHEALTHY: <service> is <state>` to the journal. The health-check unit **does not restart anything** — it only observes and logs. Recovery is `hermes-gateway.service`'s own `Restart=on-failure`, or manual intervention if that has already been exhausted (systemd's default restart burst limit applies — repeated failures within a short window stop auto-restart and require `systemctl reset-failed` plus a manual `systemctl start` after the underlying cause is fixed).

## Alerting

Not implemented by this package — `journalctl -u hermes-healthcheck.service` is the source of truth until an alerting integration is separately authorized. Do not assume a silent failure is impossible; check the journal, or wire an alert, before relying on this check for unattended operation.

## Verifying the check itself works

After install, deliberately stop one Compose service (`docker compose stop <service>`) and confirm the next health-check run within 5 minutes logs `UNHEALTHY`. Restart the service and confirm the following run logs `OK`. This is a one-time verification during install, not a standing test.
