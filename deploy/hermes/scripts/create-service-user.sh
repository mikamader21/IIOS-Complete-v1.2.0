#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before running on a real host.
#
# Creates the dedicated, unprivileged system user that owns every Hermes
# process and file (docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md, decision 1).
# No sudo group membership, no login shell, no SSH key is created for this user.

set -euo pipefail

SERVICE_USER="hermes"

if id "$SERVICE_USER" &>/dev/null; then
  echo "User $SERVICE_USER already exists — nothing to do."
  exit 0
fi

useradd \
  --system \
  --create-home \
  --home-dir /opt/hermes \
  --shell /usr/sbin/nologin \
  --comment "Hermes runtime service account (no interactive login, no sudo)" \
  "$SERVICE_USER"

passwd --lock "$SERVICE_USER"

echo "Created system user: $SERVICE_USER (locked password, no shell, no sudo)"
