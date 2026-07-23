# NOW

**`HERMES-DEP-001` — Secure Hermes VPS deployment package — `review`.**

Branch `feature/hermes-deployment-package`. Dependency `GOV-IMP-001` satisfied: PR #7 merged (commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`), CI verified green (4/4 checks, run `30047219545`). Task selected without asking, per the Owner's standing "no preguntes qué tarea sigue" instruction and `AUTONOMY_PROTOCOL.md`.

All eighteen design/preparation deliverables complete: `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`, `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` (Proposed), and `deploy/hermes/` — service-user and directory-bootstrap scripts, six systemd units (gateway, worker, backup service+timer, health-check service+timer), UFW firewall script + egress allowlist, secret-injection design (`env.template` with placeholders only, no real secret), the first Hermes profile (`ict-trading`, read-only, no order endpoint), and five runbooks (install, uninstall/rollback, update/rollback, backup/restore, health checks).

**No real VPS was provisioned, connected to, or modified. No script under `deploy/hermes/` was executed.** That sub-scope requires a separate, explicit Owner authorization per the task's own `owner_decision_required` split. Not marked `done` until merged and CI-verified.
