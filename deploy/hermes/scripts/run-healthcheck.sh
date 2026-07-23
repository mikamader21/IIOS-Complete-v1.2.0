#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001/HERMES-INSTALL-001-preparation.
# Review before installing.
#
# Installed to /opt/hermes/core/compose/scripts/run-healthcheck.sh and
# invoked by systemd/hermes-healthcheck.service. Observes and logs only —
# never restarts anything (see runbooks/HEALTH_CHECKS.md). Checks the ONE
# shared Hermes container and loops over every profile it currently hosts
# (docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md decision 2, 10) using the
# OFFICIAL `hermes doctor` / `hermes profile list` / `hermes -p <name>
# gateway status` commands (NousResearch/hermes-agent CLI reference,
# consulted 2026-07-23 against release v0.19.0 / tag v2026.7.20) — run
# inside the container via `docker exec`, which requires the `hermes`
# service user to be in the host's `docker` group (effectively
# root-equivalent via docker.sock — a real, accepted trade-off, distinct
# from hermes-backup.service, which no longer needs this since the topology
# reconciliation moved backups to a plain host-level tar).

set -euo pipefail

CONTAINER="hermes"
STATE_FILE="/opt/hermes/logs/healthcheck-restart-count.state"
RESTART_WARN_DELTA=3

failed=0

echo "--- Hermes health check $(date -u --iso-8601=seconds) ---"

# 1. Container running state.
if [[ "$(docker inspect --format '{{.State.Running}}' "$CONTAINER" 2>/dev/null)" != "true" ]]; then
  echo "FAIL: $CONTAINER is not running"
  failed=1
else
  echo "OK: $CONTAINER is running"
fi

# 2. Restart-loop detection via Docker's own RestartCount, compared to the
# previous run. Heuristic, not a guarantee — confirm the threshold is sane
# after observing real operation.
if docker inspect "$CONTAINER" >/dev/null 2>&1; then
  current_count="$(docker inspect --format '{{.RestartCount}}' "$CONTAINER")"
  previous_count=0
  [[ -f "$STATE_FILE" ]] && previous_count="$(cat "$STATE_FILE")"
  delta=$(( current_count - previous_count ))
  if (( delta >= RESTART_WARN_DELTA )); then
    echo "FAIL: $CONTAINER restarted $delta times since the last check (possible restart loop)"
    failed=1
  else
    echo "OK: $CONTAINER restart count stable ($current_count total, +$delta since last check)"
  fi
  echo "$current_count" > "$STATE_FILE"
else
  echo "FAIL: could not inspect $CONTAINER for restart count"
  failed=1
fi

# 3. Host disk and memory — the VPS's own resources, shared by every
# co-located profile.
disk_avail_pct="$(df -h /opt/hermes | awk 'NR==2 {print 100-$5}' | tr -d '%')"
if [[ -n "$disk_avail_pct" ]] && (( disk_avail_pct < 10 )); then
  echo "FAIL: /opt/hermes disk free below 10%"
  failed=1
else
  echo "OK: /opt/hermes disk free acceptable"
fi

mem_avail_mb="$(free -m | awk '/^Mem:/ {print $7}')"
if [[ -n "$mem_avail_mb" ]] && (( mem_avail_mb < 256 )); then
  echo "FAIL: host available memory below 256MB"
  failed=1
else
  echo "OK: host available memory acceptable (${mem_avail_mb}MB)"
fi

# 4. Container-wide diagnostics.
if ! docker exec "$CONTAINER" hermes doctor > /tmp/hermes-doctor.out 2>&1; then
  echo "FAIL: hermes doctor reported an issue — see /tmp/hermes-doctor.out"
  failed=1
else
  echo "OK: hermes doctor clean"
fi

# 5. Per-profile gateway status — loop over whatever profiles actually
# exist rather than hardcoding "onyx", so this script keeps working as
# ict-trading/developer/research/knowledge/blockchain/regulation profiles
# are added later (docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md decision 10).
profiles="$(docker exec "$CONTAINER" hermes profile list 2>/dev/null | awk '{print $1}' | grep -v '^$' || true)"
if [[ -z "$profiles" ]]; then
  echo "INFO: no profiles created yet (expected before any activation)"
else
  while IFS= read -r profile; do
    if ! docker exec "$CONTAINER" hermes -p "$profile" gateway status > "/tmp/hermes-gateway-status-${profile}.out" 2>&1; then
      echo "FAIL: hermes -p ${profile} gateway status reported an issue — see /tmp/hermes-gateway-status-${profile}.out"
      failed=1
    else
      echo "OK: profile '${profile}' gateway status reported healthy"
    fi
  done <<< "$profiles"
fi

# 6. HERMES_HOME (the shared /opt/data volume) accessibility — confirm it
# is actually writable from inside the container (catches a silent
# permissions regression from a host-side ownership/permission change).
if ! docker exec "$CONTAINER" sh -c 'test -w /opt/data'; then
  echo "FAIL: /opt/data is not writable inside $CONTAINER"
  failed=1
else
  echo "OK: /opt/data writable"
fi

# 7. Recent logs — surface the tail for the operator, do not parse it
# automatically (log format is not stable enough to assert on here).
echo "--- recent logs (docker logs, last 20 lines) ---"
docker logs --tail 20 "$CONTAINER" || echo "WARN: could not retrieve recent logs"

# 8. Egress reachability to allowed providers only. Not implemented: no
# model/data provider has been selected yet (work/BLOCKED.md), so there is
# no real hostname to check against deploy/hermes/firewall/egress-allowlist.md
# without guessing one. Add a concrete check here once a provider is
# selected — do not fabricate a hostname in the meantime.
echo "SKIPPED: egress-reachability-to-allowed-providers check — no provider selected yet (work/BLOCKED.md)"

if (( failed )); then
  echo "Hermes health check FAILED $(date -u --iso-8601=seconds)"
  exit 1
fi

echo "Hermes health check OK $(date -u --iso-8601=seconds)"
