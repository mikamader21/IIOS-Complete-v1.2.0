#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before installing.
#
# Installed to /opt/hermes/core/compose/scripts/run-healthcheck.sh and
# invoked by systemd/hermes-healthcheck.service. Observes and logs only —
# never restarts anything (see runbooks/HEALTH_CHECKS.md).

set -euo pipefail

COMPOSE_DIR="/opt/hermes/core/compose"
cd "$COMPOSE_DIR"

unhealthy=0
while IFS= read -r line; do
  name=$(echo "$line" | awk '{print $1}')
  status=$(echo "$line" | awk '{print $2}')
  if [[ "$status" != "running" && "$status" != "healthy" ]]; then
    echo "UNHEALTHY: $name is $status"
    unhealthy=1
  fi
done < <(docker compose ps --format '{{.Name}} {{.State}}')

if [[ "$unhealthy" -eq 1 ]]; then
  echo "Hermes health check FAILED $(date -u --iso-8601=seconds)"
  exit 1
fi

echo "Hermes health check OK $(date -u --iso-8601=seconds)"
