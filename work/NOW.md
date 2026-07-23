# NOW

**`HERMES-DEP-001` — Secure Hermes VPS deployment package — `in_progress`.**

Branch `feature/hermes-deployment-package`. Dependency `GOV-IMP-001` satisfied: PR #7 merged (commit `381f525`, merge commit `bb4579bf82c6cddf65a5280e74b9327714340a45`), CI verified green (4/4 checks, run `30047219545`). Task selected without asking, per the Owner's standing "no preguntes qué tarea sigue" instruction and `AUTONOMY_PROTOCOL.md`.

Scope explicitly limited to **design and preparation only**: VPS threat model, unprivileged service user design, directory structure, filesystem isolation, `terminal.cwd`/`terminal.home_mode` configuration design, egress allowlist, firewall design, systemd unit design, backups, logs, health checks, update/rollback procedure, profile separation, secret-injection design with no real secrets, `ict-trading` profile package design, installation runbook, uninstall/rollback runbook.

Must **not** connect to, provision, or modify any real VPS — that sub-scope requires separate Owner authorization per the task's own `owner_decision_required` split (`false` for design/preparation, `true` for any real VPS action).
