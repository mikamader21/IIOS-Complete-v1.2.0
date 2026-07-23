#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before installing.
#
# Installed to /opt/hermes/core/compose/scripts/run-healthcheck.sh and
# invoked by systemd/hermes-healthcheck.service. Observes and logs only —
# never restarts anything (see runbooks/HEALTH_CHECKS.md). Uses the
# OFFICIAL `hermes doctor`, `hermes status`, and `hermes gateway status`
# commands (NousResearch/hermes-agent CLI reference, consulted 2026-07-23
# against release v0.19.0, 2026-07-20) instead of inspecting Docker
# process state alone.

set -euo pipefail

COMPOSE_DIR="/opt/hermes/core/compose"
PROFILE="ict-trading"
CONTAINER="hermes-${PROFILE}"
STATE_FILE="/opt/hermes/logs/healthcheck-restart-count.state"
RESTART_WARN_DELTA=3

cd "$COMPOSE_DIR"
failed=0

echo "--- Hermes health check $(date -u --iso-8601=seconds) ---"

# 1. Process/service state (Docker's own view).
if ! docker compose ps --status running --format '{{.Name}}' | grep -qx "$CONTAINER"; then
  echo "FAIL: $CONTAINER is not in a running state"
  failed=1
else
  echo "OK: $CONTAINER is running"
fi

# 2. Restart-loop detection via Docker's own RestartCount, compared to the
# previous run. This is a heuristic, not a guarantee — confirm the
# threshold is sane after observing real operation.
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

# 3. Host disk and memory — the VPS's own resources, not just the
# container's, since exhausting either affects every service on the host.
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

# 4. Application-level checks, run inside the container.
if ! docker compose exec -T "$PROFILE" hermes doctor > /tmp/hermes-doctor.out 2>&1; then
  echo "FAIL: hermes doctor reported an issue — see /tmp/hermes-doctor.out"
  failed=1
else
  echo "OK: hermes doctor clean"
fi

if ! docker compose exec -T "$PROFILE" hermes gateway status > /tmp/hermes-gateway-status.out 2>&1; then
  echo "FAIL: hermes gateway status reported an issue — see /tmp/hermes-gateway-status.out"
  failed=1
else
  echo "OK: hermes gateway status reported healthy"
fi

# 5. HERMES_HOME accessibility — confirm the mounted volume is actually
# writable from inside the container (catches a silent permissions
# regression from a host-side ownership/permission change).
if ! docker compose exec -T "$PROFILE" sh -c 'test -w "$HERMES_HOME" 2>/dev/null || test -w /opt/data'; then
  echo "FAIL: HERMES_HOME is not writable inside $CONTAINER"
  failed=1
else
  echo "OK: HERMES_HOME writable"
fi

# 6. Recent logs — surface the tail for the operator, do not parse it
# automatically (log format is not stable enough to assert on here).
echo "--- recent logs (docker compose logs, last 20 lines) ---"
docker compose logs --tail 20 "$PROFILE" || echo "WARN: could not retrieve recent logs"

# 7. Egress reachability to allowed providers only. Not implemented: no
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
