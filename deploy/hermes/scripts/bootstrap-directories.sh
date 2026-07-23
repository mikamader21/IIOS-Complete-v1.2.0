#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before running on a real host.
#
# Creates the /opt/hermes/ tree described in deploy/hermes/directory-layout.md,
# with ownership and permissions applied immediately after creation. Requires
# deploy/hermes/scripts/create-service-user.sh to have run first.

set -euo pipefail

SERVICE_USER="hermes"
BASE="/opt/hermes"

if ! id "$SERVICE_USER" &>/dev/null; then
  echo "Service user $SERVICE_USER does not exist — run create-service-user.sh first." >&2
  exit 1
fi

directories=(
  "$BASE/core/compose"
  "$BASE/core/secrets"
  "$BASE/profiles"
  "$BASE/backups"
  "$BASE/logs"
)

for dir in "${directories[@]}"; do
  mkdir -p "$dir"
  chown "$SERVICE_USER:$SERVICE_USER" "$dir"
  chmod 0750 "$dir"
done

# secrets/ is stricter than the rest of the tree.
chmod 0700 "$BASE/core/secrets"

echo "Bootstrapped $BASE (owner $SERVICE_USER, 0750 default, 0700 for core/secrets)"
echo "Create a profile with: mkdir -p $BASE/profiles/<name>/{workspace,state} && chown -R $SERVICE_USER:$SERVICE_USER $BASE/profiles/<name> && chmod 0750 $BASE/profiles/<name> $BASE/profiles/<name>/workspace $BASE/profiles/<name>/state"
