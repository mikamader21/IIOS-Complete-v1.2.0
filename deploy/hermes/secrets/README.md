# Secret injection design

No real secret exists anywhere in this repository or in `deploy/hermes/`. This document specifies how a secret reaches a running Hermes container without ever passing through Claude, Git, or CI.

## Flow

1. `env.template` in this directory lists every environment variable a profile's Compose service expects, each set to a placeholder.
2. On the real host, the Owner (or, once selected, whatever KMS/HSM/Vault product `docs/23_CAPABILITY_MODEL.md`'s "Open questions" resolves) creates `/opt/hermes/core/secrets/.env` by copying `env.template` and replacing every placeholder with a real value, directly on the host — never through a file committed to this repository, never through a chat message, never through a Claude Code tool call.
3. `.env` is `chmod 0600`, `chown hermes:hermes`. `deploy/hermes/directory-layout.md` fixes `core/secrets/` itself at `0700`.
4. Every systemd unit that needs a secret loads it via `EnvironmentFile=/opt/hermes/core/secrets/.env` (see `systemd/hermes-gateway.service`, `systemd/hermes-backup.service`). systemd passes these as process environment to the container; no script in this package echoes, logs, or transmits a value from that file.
5. `.gitignore` at the repository root must exclude any path matching `deploy/hermes/**/.env` before this package is ever used against a real host — added as part of this task (see the diff).

## Rules

- No script under `deploy/hermes/` reads `.env` for any purpose other than passing it to `docker compose` / systemd as an environment source.
- No secret value is ever a command-line argument (visible in `ps`); every consumer reads from the environment or the `EnvironmentFile=`-loaded file.
- Rotation follows whatever cadence the eventual KMS/HSM/Vault selection defines (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md` already fixed a 90-day rotation for capability-signing keys as a related precedent — infrastructure secrets are not required to match that cadence, but should not exceed it without a documented reason).
- `scripts/verify_foundation.py`'s secret scanner runs over this repository on every CI run; this package is designed so that scanner should never find a match here — if it ever does, that is a packaging bug, not a false positive to suppress.
