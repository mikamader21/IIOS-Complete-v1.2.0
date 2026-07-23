#!/usr/bin/env bash
# Template — not executed by HERMES-DEP-001. Review before running on a real host.
#
# Default-deny inbound and outbound, then an explicit allowlist. Matches
# docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md decisions 3-4 and
# docs/10_INFRASTRUCTURE.md ("no public database/Redis/Hermes ports").
#
# TUNNEL_INTERFACE and OPERATOR_CIDR must be set to real values before this
# script is ever run — placeholders here are intentionally invalid so the
# script fails closed if run unmodified.

set -euo pipefail

TUNNEL_INTERFACE="${TUNNEL_INTERFACE:-tailscale0}"
OPERATOR_SSH_CIDR="${OPERATOR_SSH_CIDR:-__SET_BEFORE_USE__}"

if [[ "$OPERATOR_SSH_CIDR" == "__SET_BEFORE_USE__" ]]; then
  echo "OPERATOR_SSH_CIDR is not set — refusing to apply firewall rules with an undefined SSH source." >&2
  exit 1
fi

ufw --force reset
ufw default deny incoming
ufw default deny outgoing

# Inbound: SSH only from the operator's known network; everything else
# arrives over the private tunnel interface, not the public one.
ufw allow in on "$TUNNEL_INTERFACE"
ufw allow from "$OPERATOR_SSH_CIDR" to any port 22 proto tcp

# Outbound: DNS, NTP, the tunnel, and the package/model-provider endpoints
# in egress-allowlist.md. This script intentionally does not enumerate the
# per-provider allowlist inline — see egress-allowlist.md and keep it as
# the single source of truth to avoid drift between the doc and the rules.
ufw allow out on "$TUNNEL_INTERFACE"
ufw allow out 53/udp
ufw allow out 53/tcp
ufw allow out 123/udp
ufw allow out 443/tcp   # HTTPS only — see egress-allowlist.md for destinations
ufw allow out 80/tcp    # required only during install/update for package fetches

ufw --force enable
ufw status verbose
