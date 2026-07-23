# Hermes egress allowlist

Default-deny outbound. This table is the source of truth `firewall/apply-ufw-rules.sh` implements; if the two ever disagree, this document wins and the script must be updated to match.

| Destination | Port/proto | Purpose | Always-on? |
|---|---|---|---|
| Tunnel interface (Tailscale or equivalent) | all, tunnel interface only | Owner/operator private access to the gateway | Yes |
| DNS resolver | 53/udp, 53/tcp | Name resolution | Yes |
| NTP | 123/udp | Clock sync — audit timestamps and TLS both depend on correct time | Yes |
| Model-provider API endpoints | 443/tcp | Whatever model routing (`docs/06_MODEL_ROUTING.md`, `docs/MODEL_ROUTING.md`) selects for the active profile | Yes, scoped to the specific provider hostnames once selected |
| OS package registry (apt) | 443/tcp, 80/tcp | Security patching per the upgrade policy | Install/update windows only |
| Docker image registry | 443/tcp | Pulling pinned Hermes/Compose image tags | Install/update windows only |
| Everything else | — | — | Denied |

Notes:

- No rule in this table or in `apply-ufw-rules.sh` opens an inbound port for Hermes, the database, or the gateway on the public interface — those are reachable only via the tunnel interface (`docs/10_INFRASTRUCTURE.md` — "no public database/Redis/Hermes ports").
- Model-provider hostnames are left unresolved here deliberately — `docs/MODEL_ROUTING.md` and `config/model-registry.json` are the source of truth for which providers are in use, and hard-coding hostnames in a firewall doc that predates any real provider selection would drift.
- If a future profile needs a new destination, it is added here first, then to the script — never the reverse.
