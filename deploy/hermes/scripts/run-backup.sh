#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before installing.
#
# Uses the OFFICIAL `hermes backup` command (confirmed against
# NousResearch/hermes-agent's CLI reference and community-verified `-o`
# output flag, consulted 2026-07-23 against release v0.19.0, 2026-07-20)
# instead of a raw tar of arbitrary host paths — hermes backup already
# knows what belongs in a coherent backup (config, skills, sessions, data)
# and excludes the agent codebase itself, so it will not sweep up a cache
# or virtualenv the way a naive `tar` of the whole state directory could.
#
# Installed to /opt/hermes/core/compose/scripts/run-backup.sh and invoked
# by systemd/hermes-backup.service on the HOST — it shells into the
# running container via `docker compose exec`, it does not run `hermes`
# directly (the CLI is not installed on the host, only inside the image).

set -euo pipefail

COMPOSE_DIR="/opt/hermes/core/compose"
PROFILE="ict-trading"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
# -o targets a path under /opt/data (the container's HERMES_HOME, bind-
# mounted from the host's state/ directory per
# deploy/hermes/core/docker-compose.yml.template) so the resulting archive
# is visible on the host without a separate `docker cp` step.
CONTAINER_OUTPUT="/opt/data/backups/hermes-backup-${STAMP}.zip"
HOST_STATE_DIR="/opt/hermes/profiles/${PROFILE}/state"
HOST_BACKUPS_DIR="/opt/hermes/backups"

cd "$COMPOSE_DIR"
mkdir -p "${HOST_STATE_DIR}/backups"

# --quick is a state-only snapshot; a full (non --quick) backup is used
# here instead so config, skills, and sessions are captured, not only
# state — confirm this trade-off (full vs --quick) against the observed
# archive size/time before relying on this in a real recurring job.
docker compose exec -T "$PROFILE" hermes backup -o "$CONTAINER_OUTPUT"

mkdir -p "$HOST_BACKUPS_DIR"
mv "${HOST_STATE_DIR}/backups/hermes-backup-${STAMP}.zip" "${HOST_BACKUPS_DIR}/"

echo "Backup complete: ${HOST_BACKUPS_DIR}/hermes-backup-${STAMP}.zip"
echo "Transport to an external, encrypted destination is not implemented here — select a destination/tool (work/BLOCKED.md) and extend this script before first real use."
echo "NOTE: the exact internal container user hermes-agent runs as, and whether it can write to /opt/data/backups/ with the permissions this script assumes, was not independently confirmed against a running instance during this design task — verify with 'docker compose exec ict-trading whoami' and a real dry run before enabling the schedule."
