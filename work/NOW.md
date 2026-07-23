# NOW

**`HERMES-DEP-001` — Secure Hermes VPS deployment package — `review`.**

Branch `feature/hermes-deployment-package`. Dependency `GOV-IMP-001` satisfied: PR #7 merged (commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`), CI verified green (4/4 checks, run `30047219545`). Task selected without asking, per the Owner's standing "no preguntes qué tarea sigue" instruction and `AUTONOMY_PROTOCOL.md`.

All eighteen design/preparation deliverables complete and then **audited by the Owner against the real `NousResearch/hermes-agent` product** (v0.19.0, 2026-07-20, consulted 2026-07-23) before merge — the audit found and required fixing a fabricated "worker" systemd unit, a gateway-supervising unit duplicating Docker's own `restart: unless-stopped`, an invalid `terminal.home_mode` value, an ambiguous IIOS-manifest-vs-Hermes-config framing, a raw-tar backup duplicating the official `hermes backup` command, and an unsafe default-apply firewall script. All corrected — see `docs/31_HERMES_DEPLOYMENT_PACKAGE.md` — "Corrections after upstream audit".

Package: `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`, `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` (Proposed), and `deploy/hermes/` — service-user and directory-bootstrap scripts, a pinned single-container-per-profile Docker Compose template, two systemd timers (backup via the official `hermes backup` CLI, health check via `hermes doctor`/`hermes gateway status`), a dry-run-by-default UFW firewall script with a rollback safety net, a three-file secret-injection design (no real secret), the first Hermes deployment (`ict-trading`, read-only, no order endpoint, `terminal.backend: local`), and five runbooks. A new `hermes-deployment-tests` CI job validates the package (`bash -n`, ShellCheck, `systemd-analyze verify`, line-endings, credential-shape scan, financial-execution structural check).

Status:
```text
HERMES-DEP-001: in review
VPS installation: not authorized
Hermes runtime: not installed
ict-trading profile: specified, not activated
```

**No real VPS was provisioned, connected to, or modified. No script under `deploy/hermes/` was executed against a real host.** That sub-scope requires a separate, explicit Owner authorization. Not marked `done` until merged and CI-verified.
