#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before installing.
#
# Installed to /opt/hermes/core/compose/scripts/run-backup.sh during
# INSTALL.md and invoked by systemd/hermes-backup.service. File-level backup
# of core/ and profiles/ (never core/secrets/ — see runbooks/BACKUP_RESTORE.md
# for why). Backup tool and destination are an open Owner decision
# (work/BLOCKED.md); this script only defines the source set and the
# exclusion, not the transport.

set -euo pipefail

SOURCE_PATHS=(
  "/opt/hermes/core/compose"
  "/opt/hermes/profiles"
)
EXCLUDE=(
  "--exclude=/opt/hermes/core/secrets"
)
STAGING="/opt/hermes/backups/$(date -u +%Y%m%dT%H%M%SZ)"

mkdir -p "$STAGING"
tar "${EXCLUDE[@]}" -czf "$STAGING/hermes-backup.tar.gz" "${SOURCE_PATHS[@]}"

echo "Staged backup at $STAGING/hermes-backup.tar.gz"
echo "Transport to the encrypted external destination is not implemented here — select a destination/tool (work/BLOCKED.md) and extend this script before first real use."
