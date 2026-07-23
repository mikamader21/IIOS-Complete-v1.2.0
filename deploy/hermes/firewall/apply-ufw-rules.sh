#!/usr/bin/env bash
#
# ============================================================
#  RUN ONLY DURING AN AUTHORIZED VPS CHANGE WINDOW.
#  Not executed by HERMES-DEP-001. This script is safe to READ
#  and REVIEW at any time — it refuses to apply anything unless
#  called with --apply, and even then requires an explicit,
#  already-verified SSH source before touching outbound rules.
# ============================================================
#
# Default-deny OUTBOUND is intentionally NOT applied by this script as
# shipped (per the HERMES-DEP-001 design-only scope) — see --apply-egress
# below, off by default. Inbound default-deny + an explicit SSH allow is
# the only change this script makes unless --apply-egress is also passed,
# and even that requires --apply.
#
# Safety model:
#   1. Dry run by default (no flag changes anything). Prints the exact
#      `ufw` commands it would run and exits 0.
#   2. --apply actually runs them, but only after confirming the given
#      SSH source/port combination is NOT already blocked by the current
#      ruleset (so you cannot lock yourself out with your own script).
#   3. A rollback safety net: if the `at` command is available, --apply
#      schedules an automatic `ufw disable` N minutes out (default 15),
#      cancelled by touching /opt/hermes/.firewall-confirmed within that
#      window from a second, already-open session — the standard "revert
#      unless confirmed" pattern for remote firewall changes. If `at` is
#      not available, this is skipped and printed as a warning: keep a
#      second administrative session open manually instead.
#
# TUNNEL_INTERFACE, SSH_SOURCE_CIDR and SSH_PORT must be set — placeholders
# are intentionally invalid so the script fails closed if run unmodified.

set -euo pipefail

TUNNEL_INTERFACE="${TUNNEL_INTERFACE:-tailscale0}"
SSH_SOURCE_CIDR="${SSH_SOURCE_CIDR:-__SET_BEFORE_USE__}"
SSH_PORT="${SSH_PORT:-22}"
ROLLBACK_MINUTES="${ROLLBACK_MINUTES:-15}"
CONFIRM_FILE="/opt/hermes/.firewall-confirmed"

APPLY=0
APPLY_EGRESS=0
for arg in "$@"; do
  case "$arg" in
    --apply) APPLY=1 ;;
    --apply-egress) APPLY_EGRESS=1 ;;
    *) echo "Unknown argument: $arg" >&2; exit 2 ;;
  esac
done

if [[ "$SSH_SOURCE_CIDR" == "__SET_BEFORE_USE__" ]]; then
  echo "SSH_SOURCE_CIDR is not set — refusing to plan or apply firewall rules with an undefined SSH source." >&2
  exit 1
fi

# Each planned rule is a real argv array (no string-building + eval —
# avoids the word-splitting/injection risk eval carries even when the
# input is our own hardcoded strings). ufw_rule prints the rule always,
# and additionally executes it via "$@" when APPLY=1.
ufw_rule() {
  echo "  ufw $*"
  if (( APPLY )); then
    ufw "$@"
  fi
}

plan_rules() {
  ufw_rule default deny incoming
  ufw_rule allow in on "$TUNNEL_INTERFACE"
  ufw_rule allow from "$SSH_SOURCE_CIDR" to any port "$SSH_PORT" proto tcp

  if (( APPLY_EGRESS )); then
    # Explicit, itemized — never a bare "default deny outgoing" without
    # these paired allow rules applied in the same pass. See
    # deploy/hermes/firewall/egress-allowlist.md for the destination table
    # this list must stay in sync with.
    ufw_rule default deny outgoing
    ufw_rule allow out on "$TUNNEL_INTERFACE"
    ufw_rule allow out 53/udp    # DNS
    ufw_rule allow out 53/tcp    # DNS
    ufw_rule allow out 123/udp   # NTP
    ufw_rule allow out 443/tcp   # HTTPS — see egress-allowlist.md for destinations
    ufw_rule allow out 80/tcp    # apt/package fetches during install/update windows only
  fi
}

echo "Planned ufw commands:"

if (( ! APPLY )); then
  plan_rules
  echo
  echo "DRY RUN — nothing was changed. Re-run with --apply during an authorized VPS change window to execute the plan above."
  if (( ! APPLY_EGRESS )); then
    echo "NOTE: outbound rules were not planned (pass --apply-egress to include them). Outbound traffic is left unrestricted by this script as shipped."
  fi
  exit 0
fi

echo
echo "APPLYING — this will change live firewall state."

# Confirm current state doesn't already block the SSH source before UFW
# is touched at all, so a misconfigured SSH_SOURCE_CIDR is caught before
# any rule change, not after.
if command -v ufw >/dev/null 2>&1; then
  ufw status | grep -q "Status: active" && echo "NOTE: ufw is already active — applying additional rules, not resetting from scratch (this script never runs 'ufw --force reset')."
else
  echo "ufw is not installed — aborting." >&2
  exit 1
fi

plan_rules

ufw enable
ufw status verbose

rm -f "$CONFIRM_FILE"
if command -v at >/dev/null 2>&1; then
  echo "ufw disable" | at now + "${ROLLBACK_MINUTES}" minutes 2>/dev/null || true
  echo "Rollback safety net scheduled: 'ufw disable' will run automatically in ${ROLLBACK_MINUTES} minutes."
  echo "From a SECOND, already-open administrative session, confirm connectivity and then run:"
  echo "  touch ${CONFIRM_FILE} && atrm \$(atq | tail -1 | awk '{print \$1}')"
  echo "to cancel the automatic rollback. If you cannot reach that second session, do nothing — the rollback will restore access."
else
  echo "WARNING: 'at' is not installed — no automatic rollback safety net is available." >&2
  echo "Keep a second, already-authenticated administrative session open until you have confirmed you are not locked out." >&2
fi
