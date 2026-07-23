#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001/HERMES-INSTALL-001-preparation.
# Review before installing.
#
# Backs up the ONE shared Hermes data volume (/opt/hermes/data on the host,
# bind-mounted to /opt/data in the container), covering every co-located
# profile in a single archive. This is a host-level file copy, not a
# `docker exec ... hermes backup` call — the topology reconciliation
# (docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md Amendment 2) confirmed
# that /opt/hermes/data IS Hermes' entire mutable state (config, .env,
# sessions, memories, skills, per-profile subtrees); the immutable
# application code, venv, and node_modules live inside the image itself at
# /opt/hermes, never on this bind-mounted volume, so a plain tar of
# /opt/hermes/data cannot accidentally sweep up a cache or venv — the
# earlier per-profile-container design used the official `hermes backup`
# CLI specifically to avoid that risk; this design achieves the same
# guarantee structurally, without needing docker exec or the `docker`
# group membership trade-off that entailed.
#
# WARNING: this archive contains live secrets once any profile is actually
# activated with real credentials — Hermes' own .env files are part of its
# state by design (upstream: "Secrets and tokens -> ~/.hermes/.env", backed
# up and restorable). Nothing is activated as of this design task, so no
# real secret exists yet, but treat the resulting archive as sensitive from
# the first real activation onward — see runbooks/BACKUP_RESTORE.md.

set -euo pipefail

DATA_DIR="/opt/hermes/data"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
HOST_BACKUPS_DIR="/opt/hermes/backups"

if [[ ! -d "$DATA_DIR" ]]; then
  echo "FAIL: $DATA_DIR does not exist — nothing to back up." >&2
  exit 1
fi

mkdir -p "$HOST_BACKUPS_DIR"
tar -czf "${HOST_BACKUPS_DIR}/hermes-data-${STAMP}.tar.gz" -C "$(dirname "$DATA_DIR")" "$(basename "$DATA_DIR")"

echo "Backup complete: ${HOST_BACKUPS_DIR}/hermes-data-${STAMP}.tar.gz"
echo "Transport to an external, encrypted destination is not implemented here — select a destination/tool (work/BLOCKED.md) and extend this script before first real use."
echo "NOTE: from the first real profile activation onward this archive contains live secrets (each activated profile's .env) — encrypt at rest and restrict access accordingly."
