# IIOS Hermes VPS Deployment Package (HERMES-DEP-001)

**Status:** Design/preparation complete, audited against the real upstream product, in review. No real VPS provisioned, connected to, or modified. Hermes remains **not integrated** (`docs/TOOL_REGISTRY.md`).
**Parent authority:** `docs/03_GOVERNANCE_SECURITY.md` (Hermes baseline), `docs/10_INFRASTRUCTURE.md` (VPS MVP direction), `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`, `docs/HANDOFF_PROTOCOL.md`, `MASTER_IMPLEMENTATION_PROGRAM.md` Phase 6.

## Scope

This document and the package under `deploy/hermes/` cover exactly the eighteen deliverables listed for `HERMES-DEP-001` in `BACKLOG.md`. Every artifact is a template, script, or document reviewed and version-controlled ahead of any real infrastructure — none has been executed against a host. Connecting to or modifying a real VPS is a separate, explicit Owner decision (`work/BLOCKED.md`) and a separate task.

## Corrections after upstream audit

The first draft of this package was written against this repository's own general infrastructure docs (`docs/10_INFRASTRUCTURE.md`), without checking the real `NousResearch/hermes-agent` product. An Owner-directed pre-merge audit required that check. Consulted 2026-07-23 against release **v0.19.0** (2026-07-20) — the official docs site (`hermes-agent.nousresearch.com/docs/`), the CLI reference, and `cli-config.yaml.example` in the `NousResearch/hermes-agent` repository. Corrections made as a result:

- Removed a fabricated `hermes-worker.service` — there is no "worker" process or CLI subcommand in the real product.
- Removed a custom `hermes-gateway.service` that wrapped `docker compose up/down` — Docker's own `restart: unless-stopped`, together with the Docker daemon (already systemd-managed on Ubuntu), is the officially documented supervision mechanism for the Docker deployment path. A custom unit duplicated it.
- Added a real, pinned `deploy/hermes/core/docker-compose.yml.template`, matching the official single-container example, adapted to one container per IIOS profile for host-level isolation.
- Corrected `terminal.home_mode` from an invented `profile_scoped` to the real value `profile` (confirmed values: `auto`, `real`, `profile`).
- Reconsidered and reversed `terminal.backend` for `ict-trading` from `docker` to `local`, to avoid requiring a host `docker.sock` mount into the Hermes container (see `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` amendment).
- Reframed `deploy/hermes/profiles/ict-trading.profile.json` explicitly as an **IIOS deployment manifest**, distinct from Hermes' own `config.yaml` — added `deploy/hermes/profiles/ict-trading.config.yaml.template` as the real-format counterpart, and documented the materialization step.
- Rewrote the backup script to shell out to the official `hermes backup` command instead of a raw `tar` of arbitrary host paths.
- Rewrote the health-check script to use `hermes doctor` and `hermes gateway status` in addition to Docker-level process checks, host disk/memory, and a restart-count heuristic.
- Rewrote the firewall script to be dry-run by default, requiring `--apply` (and separately `--apply-egress` for outbound rules), with a pre-flight SSH-source check and an `at`-based rollback safety net.
- Removed an `eval`-based command dispatch in the firewall script in favor of real argument arrays.
- Added a `hermes-deployment-tests` CI job (Linux-only) running `bash -n`, ShellCheck, `systemd-analyze verify` (against a `hermes` user and stub scripts staged only on the ephemeral CI runner — never a real host), JSON/line-ending checks, a credential-shape scan, and a check that the `ict-trading` manifest structurally forbids financial execution.
- Set the executable bit on every `.sh` file in the package (previously `100644`).

Full detail on each point is in the affected file's own comments and in `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`'s amendment section. ADR-0013 remains **Proposed**.

## 1. VPS threat model

| Threat | Vector | Mitigation in this package |
|---|---|---|
| Remote compromise via exposed service | Public Hermes/dashboard port | No public listener; ports bound only to the tunnel interface address (§7, `deploy/hermes/firewall/`) |
| Lateral movement after a profile is compromised | Shared filesystem/HERMES_HOME across profiles | One container per profile, each with its own host directory as its entire HERMES_HOME (§4, §15) |
| Secret exfiltration | Committed credentials, forwarded env vars, verbose logs | No secret ever committed; three-file secret design (§14); empty `docker_forward_env` by default |
| Data exfiltration via egress | Unrestricted outbound traffic | Egress allowlist available via `--apply-egress`, off by default in this design-only task (§7) |
| Unbounded command execution | An overly permissive terminal backend | `terminal.backend: local` for the read-only `ict-trading` profile — no `docker.sock` mount required (§6) |
| Silent service failure | No supervision, no alerting | Docker `restart: unless-stopped` + a health-check timer using real `hermes doctor`/`gateway status` (§10, §11) |
| Unrecoverable data loss | No backup, or an untested backup | Scheduled `hermes backup` (official command), documented restore + restore-drill requirement (§9) |
| Privilege escalation from Hermes to host | Hermes running as root | Dedicated unprivileged `hermes` user (§2) — **with a documented exception**: that user must be in the host's `docker` group to run `docker compose exec` for backup/health-check, which is itself effectively root-equivalent (docker.sock access). No alternative avoiding this was identified without giving up exec-based automation. |
| Firewall change locks out the operator | A firewall script that applies default-deny without a safety net | Dry-run by default, pre-flight SSH-source check, `at`-based automatic rollback (§8) |
| Unbounded financial/order action | A future trading profile executing a real order | `ict-trading` is read-only only; CI structurally checks the manifest forbids order/withdrawal/deposit/transfer actions (§16) |
| Untested or silent rollback | Update breaks the service with no recovery path | Pinned image tags, documented rollback runbook (§12, §17) |

Residual risk: this threat model covers the deployment package itself, not Hermes' own application-level vulnerabilities (patched via the pinned-version update policy) or Governance Core's production cryptography, which remains explicitly unimplemented (`docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md`). The `docker` group membership trade-off above is a real, accepted residual risk pending a better alternative, not a mitigated one.

## 2. Unprivileged service user

`deploy/hermes/scripts/create-service-user.sh` creates a dedicated system user, `hermes`, with a locked password, no login shell of consequence, and no `sudo` group membership. It must additionally be added to the `docker` group to run `docker compose exec` for the backup/health-check jobs — see the threat model entry above for why that is a real, not cosmetic, privilege.

## 3. Directory structure

`deploy/hermes/directory-layout.md` for the full tree, `deploy/hermes/scripts/bootstrap-directories.sh` for the template that creates it.

## 4. Filesystem isolation

Each profile is its own container with its own host directory mounted as its entire `HERMES_HOME` (`/opt/hermes/profiles/<profile>/state` → `/opt/data`, the official Docker volume target). No profile's container mounts another profile's directory, `core/secrets/`, or any host path outside `/opt/hermes/`. This is a deliberate departure from Hermes' own internal multi-profile-per-installation feature (`~/.hermes/profiles/<name>/`), which would share one container/HERMES_HOME across profiles and would not give host-level isolation (`docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md` decision 6).

## 5. `terminal.cwd` / `terminal.home_mode`

Real, confirmed upstream keys. `deploy/hermes/profiles/ict-trading.config.yaml.template` sets `terminal.cwd: "/opt/data/workspace"` (absolute, inside the container — never the default `"."`) and `terminal.home_mode: "profile"` (forces `HOME={HERMES_HOME}/home` for subprocesses — the real value, not the invented `profile_scoped` from the first draft).

## 6. Terminal backend

`terminal.backend: "local"` for `ict-trading` — not `"docker"`. See the amendment in `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`: the `docker` backend would require mounting the host's `docker.sock` into the Hermes container, a privilege expansion this read-only profile does not need. `docker_forward_env: []` — empty by default, the real upstream key (confirmed in `cli-config.yaml.example`), matching `docs/03_GOVERNANCE_SECURITY.md`'s baseline.

## 7. Egress allowlist

Design documented in `deploy/hermes/firewall/egress-allowlist.md`. Not applied by default — `apply-ufw-rules.sh` requires both `--apply` and `--apply-egress`.

## 8. Firewall design

`deploy/hermes/firewall/apply-ufw-rules.sh` — dry-run by default (prints the plan, changes nothing), `--apply` to execute, pre-flight check that the configured SSH source isn't already blocked, an `at`-based automatic rollback if `at` is available (with an explicit warning if it is not), and a visible "RUN ONLY DURING AN AUTHORIZED VPS CHANGE WINDOW" banner. Never runs `ufw --force reset`.

## 9. Backups

`hermes-backup.timer` → `hermes-backup.service` → `deploy/hermes/scripts/run-backup.sh`, which runs the **official** `hermes backup` command inside the running container via `docker compose exec` and moves the resulting archive to `/opt/hermes/backups/`. Transport to an external, encrypted destination is not implemented — destination/tool selection is an open Owner decision (`work/BLOCKED.md`). Restore procedure and the restore-drill requirement: `deploy/hermes/runbooks/BACKUP_RESTORE.md`.

## 10. Logs

Docker's `json-file` log driver (rotation configured at the Compose service level) plus `docker compose logs` surfaced by the health check. systemd unit logs go to the journal.

## 11. Health checks

`hermes-healthcheck.timer` → `hermes-healthcheck.service` → `deploy/hermes/scripts/run-healthcheck.sh`, which checks: container running state, a restart-count heuristic (possible restart loop), host disk and memory, `hermes doctor`, `hermes gateway status`, `HERMES_HOME` writability, and surfaces the last 20 log lines. It never restarts anything — recovery is Docker's `restart: unless-stopped`. Egress-reachability-to-allowed-providers is explicitly left unimplemented (no model/data provider selected yet — `work/BLOCKED.md`) rather than checked against a guessed hostname. Detail: `deploy/hermes/runbooks/HEALTH_CHECKS.md`.

## 12. Update / rollback procedure

Unchanged from the first draft: follows `docs/10_INFRASTRUCTURE.md`'s upgrade policy verbatim. `deploy/hermes/runbooks/UPDATE_ROLLBACK.md`.

## 13. Profile separation

One container per profile (§4), each with its own `terminal.cwd`/`terminal.home_mode` (§5), no Compose service reaching another profile's mount.

## 14. Secret injection design

**Three files**, not one:

1. `deploy/hermes/core/compose.env.example` → `/opt/hermes/core/compose/.env` — Docker Compose's own project variable file (e.g. `TAILSCALE_IP`). Not a secret; host-specific.
2. `deploy/hermes/secrets/env.template` → `/opt/hermes/core/secrets/.env` — container/orchestration-level flags (e.g. a dashboard API key), loaded via Compose `env_file:`.
3. Hermes' own secrets, inside each profile's mounted state directory at `/opt/hermes/profiles/<profile>/state/.env` (= `HERMES_HOME/.env` inside the container) — populated via `hermes config set` or a direct out-of-band edit after first container start, per upstream docs ("Secrets and tokens -> ~/.hermes/.env").

None of the three is ever committed. Full breakdown: `deploy/hermes/secrets/README.md`.

## 15. `ict-trading` profile package

`deploy/hermes/profiles/ict-trading.profile.json` is the **IIOS deployment manifest** — not Hermes' native config format. `deploy/hermes/profiles/ict-trading.config.yaml.template` is the real `config.yaml` fragment it maps to. The install runbook's materialization step makes this mapping explicit rather than treating the JSON manifest as something Hermes itself reads. Scoped read-only (account status, balance/equity, drawdown/rules, history, alerts, calendar; no order endpoint), matching `PROJECT_STATE.md`'s proposed first domain. No standing capability — every action still requires a live Governance Core decision once Hermes is actually integrated (Phase 6), which this task does not perform. CI structurally verifies the manifest's `data_scope.prohibited` list and absence of a standing capability.

## 16. Installation runbook

`deploy/hermes/runbooks/INSTALL.md` — from a bare Ubuntu LTS VPS to a running, health-checked `ict-trading` container, including the explicit config.yaml materialization step. Not executed by this task.

## 17. Uninstall / rollback runbook

`deploy/hermes/runbooks/UNINSTALL_ROLLBACK.md` — partial rollback (revert to the previous pinned image tag) and full uninstall, gated on a verified, restorable backup before host data removal.

## 18. What this task explicitly did not do

- No VPS was provisioned, connected to, or configured.
- No script under `deploy/hermes/` was executed against a real host. The `hermes-deployment-tests` CI job stages a `hermes` user and stub scripts **only on the ephemeral, disposable GitHub Actions runner** (destroyed at job end) so `systemd-analyze verify` can meaningfully resolve `User=`/`ExecStart=` — this does not touch, resemble, or provision any real, Owner-controlled VPS, and does not install Hermes Agent itself (no `hermes` CLI is fetched or run in CI).
- No real secret, API key, or credential was created, requested, or stored anywhere in this repository.
- No VPS provider or monthly cost ceiling was selected (`work/BLOCKED.md`).
- Hermes was not installed, activated, or granted any capability. `docs/TOOL_REGISTRY.md`'s Hermes entry remains `status: not integrated`.
- The `ict-trading` profile has no live connection to any trading account, prop-firm platform, or data provider.
- `hermes gateway install --system` (the official native-install systemd path) was not used and is not part of this package — this design uses the official Docker deployment path instead, per `docs/10_INFRASTRUCTURE.md`'s existing "Docker Compose precedes Kubernetes" direction; running both would create the two-gateways-for-one-profile problem this audit explicitly checked for.

## 19. ONYX profile (added after this package's initial merge preparation)

`deploy/hermes/profiles/onyx/onyx.profile.json` and `docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md` specify a second planned Hermes profile — ONYX, the Executive Orchestrator (`BACKLOG.md` `ONYX-CORE-001`, blocked on this task merging and a real, healthy Hermes installation, among other gates). It is **specification only**: no native `config.yaml` counterpart was authored for it (unlike `ict-trading`, which has `ict-trading.config.yaml.template`), no materializer exists, and its manifest deliberately uses a different filesystem root (`/srv/iios/profiles/onyx/`) than this package's established `/opt/hermes/profiles/<name>/` convention — flagged in `docs/32` as an inconsistency to reconcile before real implementation, not silently resolved. `ict-trading` remains the only profile with a documented path toward activation review; ONYX is earlier-stage than that.

## Acceptance

See `docs/14_ACCEPTANCE_TESTS.md` — "Hermes VPS deployment package (HERMES-DEP-001)" and "ONYX Executive Orchestrator (ONYX-CORE-001, specification only)".
