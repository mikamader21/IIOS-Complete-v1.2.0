# ADR-0013 — Hermes VPS Deployment Model

Status: Ratified

## Context

`HERMES-DEP-001` (`BACKLOG.md`) asks for a secure Hermes VPS deployment package, scoped explicitly to **design and preparation only** — no real VPS is provisioned, connected to, or modified by this task. Hermes itself remains **not integrated** (`docs/TOOL_REGISTRY.md`); `docs/HANDOFF_PROTOCOL.md` and `MASTER_IMPLEMENTATION_PROGRAM.md` Phase 6 still require a separate, explicit Owner authorization before any real runtime activation. This ADR records the deployment *architecture* decision the package in `deploy/hermes/` implements, so that when Phase 6 is authorized, installation follows a pre-reviewed design rather than an ad hoc one.

This ADR does not authorize infrastructure by itself. It documents what will be built, under the constraints already ratified in `docs/03_GOVERNANCE_SECURITY.md` ("Hermes baseline") and `docs/10_INFRASTRUCTURE.md` ("VPS MVP direction"). Its ratification (below) authorizes controlled VPS deployment *preparation* specifically — not financial execution, not unrestricted agent activation, and not, by itself, connecting to a real VPS (that remains gated on `HERMES-INSTALL-001`'s own Owner-supplied VPS details).

## Verified upstream release pin

Consulted 2026-07-23, directly against three independent official sources that mutually corroborate: the GitHub releases page (marked **Latest**), the GitHub tags page, and the GitHub commit API (GPG-signature verified) — plus Docker Hub's own tag listing (image push timestamp matches the GitHub release date).

```text
Release:        Hermes Agent v0.19.0 ("The Quicksilver Release")
Release date:   2026-07-20
Git tag:         v2026.7.20 (GPG "Verified")
Upstream commit: 3ef6bbd201263d354fd83ec55b3c306ded2eb72a
Commit author:   Teknium (teknium1), Nous Research
Docker image:    nousresearch/hermes-agent
  linux/amd64:   sha256:a6ce64e2038867885c2c90f6602425e6e70293d5e6d952a0e603a99265e01c40
  linux/arm64:   sha256:ef58f7f6906a19ca4d7d77bb35711f3a9740c83c8eac692b9c038e13f27e09d5
  pushed:        2026-07-20 (Docker Hub), by definitelynotcthulhu (Nous Research org)
```

**On the prior `v0.18.2` claim:** the release commit's own diff (`3ef6bbd`) bumps `acp_registry/agent.json`'s `"version"` field from `"0.18.2"` to `"0.19.0"` — i.e. `v0.18.2` genuinely was the immediately prior release, which fully explains why a check performed even slightly before `v0.19.0` fully propagated (or against a stale cache/mirror) would have shown `v0.18.2` as latest. As of this check, `v0.19.0` / `v2026.7.20` is unambiguously latest, corroborated by three independent official sources agreeing with each other. `v0.19.0` is not a fabrication, not a branch state, and not a documentation-only reference — it is a real, GPG-signed, tagged release with a matching published Docker image.

**Deployment pins by digest**, not tag or `latest`: `nousresearch/hermes-agent@sha256:a6ce64e2038867885c2c90f6602425e6e70293d5e6d952a0e603a99265e01c40` (linux/amd64 — the presumed VPS architecture; re-verify against the actual provisioned host's architecture before first pull, and use the arm64 digest above instead if the VPS is ARM). The tag `v2026.7.20` is recorded alongside the digest for human readability and upgrade-diffing, never used alone as the deployment reference. `main` and `latest` are never deployed.

## Decision

1. **Single unprivileged service user, host-level.** The Docker daemon and its containers run under a dedicated, non-interactive host system user (`hermes`), never as an existing operator's login account. This user is separate from and must not be confused with the container-internal `hermes` user (UID 10000) the official image itself runs as — see "Real isolation boundaries" below for why that distinction matters.
2. **One official Hermes container, multiple s6-supervised profiles — reversing this ADR's original per-profile-container design.** The official image's s6-overlay (PID 1) treats each Hermes profile as a first-class supervised service (`/run/service/gateway-<name>/`), auto-restarting it on crash and reconciling its running/stopped state across container restarts — this is the officially documented and recommended pattern since the product's s6 migration, replacing the pre-s6-era "one container per profile" pattern this ADR originally adopted without checking that history. `docker compose`'s own `restart: unless-stopped` supervises the container itself; that plus the image's built-in s6 supervision is the complete, intentionally-non-duplicated supervision stack — no custom systemd unit wraps the gateway's lifecycle (unchanged from the first amendment, below).
3. **No public listener.** No Hermes port (gateway API 8642, dashboard 9119) is published by default in this task's compose template. Access, when a port is needed, is bound to the private tunnel interface address only, never `0.0.0.0`/the public interface — matching `docs/10_INFRASTRUCTURE.md` ("no public database/Redis/Hermes ports") and directly motivated by a real documented incident: the official docs cite an unauthenticated public dashboard as the entry point for a "June 2026 MCP-config persistence campaign" in which internet scanners drove an exposed agent into planting an SSH-key backdoor. Hermes' dashboard auth gate is now mandatory on any non-loopback bind (upstream hardening, confirmed 2026-07-23) — this ADR does not rely on that alone and keeps the port unpublished regardless.
4. **Default-deny inbound with an explicit allowlist; outbound egress restriction is a separate, opt-in step.** The host firewall script (`deploy/hermes/firewall/apply-ufw-rules.sh`) is dry-run by default, changes inbound rules only unless `--apply-egress` is also passed, and never runs unattended — see that script and its runbook for the safety model (pre-flight SSH-source check, rollback timer).
5. **`terminal.cwd` and `terminal.home_mode` are always explicit**, using the real, upstream-confirmed key names and values (`cli-config.yaml.example`: `home_mode` is `auto`/`real`/`profile`, not the earlier draft's invented `profile_scoped`). Per `docs/03_GOVERNANCE_SECURITY.md` ("Set explicit `terminal.cwd`"), no profile ever inherits an implicit working directory.
6. **Filesystem isolation for co-located profiles is application-layer, not OS-layer — stated plainly, not implied.** Every profile in the shared container writes to `HERMES_HOME/profiles/<name>/` (a subdirectory of the single mounted `/opt/data` volume), gets its own `config.yaml`/`.env`/sessions/memory/skills, and its own s6-supervised gateway slot — but every profile's process runs under the **same** container, **same** kernel namespaces, **same** Linux capabilities, and the **same** container-internal OS user (UID 10000, `hermes`). A compromised or misbehaving profile is not contained from its siblings by the OS or the container boundary — only by Hermes' own application-level separation (separate `HERMES_HOME` subtree, separate credentials, `HERMES_WRITE_SAFE_ROOT=/opt/data` scoping `write_file`/`patch` tool calls, which the official image sets automatically) and by keeping every co-located profile's `tools`/`capabilities` minimal. See "Real isolation boundaries" and "Future dedicated-container option" below — this is the single most consequential correction in this reconciliation, and it is a real, accepted trade-off, not a resolved one.
7. **Secrets: three distinct files, never committed.** (a) `core/compose/.env` — Docker Compose's own project variable file (e.g. the tunnel interface address), not a secret. (b) `core/secrets/.env` — container/orchestration-level flags (e.g. a dashboard API key, only if the dashboard is ever enabled), loaded via Compose `env_file:`. (c) Hermes' own secrets, inside the shared volume at `/opt/hermes/data/.env` (default profile) or `/opt/hermes/data/profiles/<name>/.env` (named profiles) — populated via `hermes config set` or a direct out-of-band edit after profile creation, per upstream docs ("Secrets and tokens -> ~/.hermes/.env"). No script in this package reads, prints, or transmits a secret value.
8. **Backups use the official `hermes backup` command**, run via `docker exec`, not a raw `tar` of arbitrary host paths — the official command already excludes the agent codebase and knows what belongs in a coherent backup.
9. **Update and rollback are pinned-digest operations.** `docs/10_INFRASTRUCTURE.md`'s existing upgrade policy (release watch → read notes/security → staging backup → pinned upgrade → tests → observation window → production approval → rollback readiness) is followed verbatim, with "pinned" now meaning pinned by image digest, not tag alone.
10. **The first profile is `onyx` (Executive Orchestrator, `docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md`), specified/not-activated, read-only.** `ict-trading` (read-only prop-firm/trading observability, no order endpoints) is a **future** specialized profile, not activated by this task. Further future profiles, co-located in the same container under the same s6-supervision model unless a specific threat-model decision moves one out (below): `developer` (`BRAIN-DEVELOPER`), `research` (`BRAIN-RESEARCH`), `knowledge` (`BRAIN-KNOWLEDGE`), `blockchain` (`BRAIN-BLOCKCHAIN`), `regulation` (`BRAIN-REGULATION`) — all already `specified`/`not_implemented` in `docs/BRAIN_REGISTRY.md`; no new Brain entries were needed for this list.

## Real isolation boundaries (what actually separates one profile from another)

Stated explicitly, per the Owner's instruction that "the fact that profiles are separate does not constitute an OS sandbox":

| Layer | Isolates profiles? | Mechanism |
|---|---|---|
| Separate `config.yaml`/`.env`/credentials | Yes | Each profile's own subtree of `/opt/data/profiles/<name>/` |
| Separate memory/sessions/skills | Yes | Same subtree mechanism |
| Separate s6 supervision slot | Yes, for crash/restart only | `/run/service/gateway-<name>/`, independent auto-restart |
| `write_file`/`patch` tool write scope | Partially | `HERMES_WRITE_SAFE_ROOT=/opt/data` (official image default) blocks writes outside the whole data volume — not scoped tighter, per-profile, by Hermes itself |
| Command execution / shell | **No** | `terminal.backend: local` runs directly inside the shared container; a profile's terminal tool (if ever granted) can, per upstream's own documentation, `cat` or overwrite files the write-guard denies via `write_file` — "defense-in-depth, not a hard boundary" (upstream's own words) |
| OS process/kernel namespace | **No** | Every profile's process is a child of the same container, same PID namespace, same UID (10000) |
| Docker/container boundary | **No, between profiles** — yes, versus the host | The container isolates the whole Hermes installation from the host; it does not isolate one profile from a sibling profile |
| Governance mediation | Not yet real | `src/iios_governance/` has no execution surface yet (`docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md`) — every profile, including `onyx`, has zero standing capability regardless of this table |

The practical consequence: co-locating profiles is safe **only** while every co-located profile's `tools`/`capabilities` stay minimal (as `onyx` v0.1's do — both empty) and while no profile holds a credential another profile's compromise could reach through the shared write-safe root. This is not a permanent posture — it is what "specified, not activated" buys us at zero infrastructure cost while nothing is live.

## Future dedicated-container option for high-risk profiles

Per the official documentation's own stated criteria for when a separate container is warranted, adopted here as this project's criteria too, to be applied via a **separate, future threat-model decision per profile** — not decided now:

- **Resource isolation** — a runaway session in one profile should not be able to exhaust resources shared with another (`--memory`/`--cpus` per container).
- **Independent image pinning** — a profile needing a different upstream image tag/digest than the rest.
- **Network segmentation** — a profile needing its own Docker network (e.g. one customer/account-facing, one internal).
- **Compliance / blast radius** — a profile whose credentials must never share an OS-level process tree with any other (the most likely reason `ict-trading` — the profile with the highest real-world consequence if compromised — eventually moves out of the shared container, even though it starts, when activated, co-located like every other profile).

No profile has been moved to this pattern by this task. This section exists so the option is documented and ready, not improvised under pressure later.

## Alternatives considered

- **Kubernetes from the start** — rejected; `docs/10_INFRASTRUCTURE.md` already decided Compose precedes Kubernetes, and a single-VPS MVP does not need an orchestrator.
- **One container per profile (this ADR's own original decision)** — reversed. It matched the product's pre-s6 recommended pattern, not its current one; the official docs now describe it as unnecessary complexity ("with s6 as PID 1, that's no longer necessary") except for the specific high-risk-isolation cases listed above.
- **Running Hermes directly under systemd without Docker** — rejected; Docker isolates the whole installation from the host, and losing that would remove the one isolation layer that IS real per the table above.
- **A custom systemd unit supervising the container's gateway lifecycle** — rejected; duplicates both Docker's `restart: unless-stopped` and the image's own built-in s6 supervision, and is not the officially documented mechanism for the Docker deployment path.
- **`terminal.backend: docker` for `onyx`** — rejected; would require mounting the host's `docker.sock` into the Hermes container (host-root-equivalent access) and, per the official security documentation, running under `docker`/`singularity`/`modal`/`daytona` backends **bypasses Hermes' own dangerous-command approval system entirely** ("the container itself is the security boundary"). `local` keeps that approval layer active — a real, non-obvious point in `local`'s favor beyond simply avoiding the `docker.sock` mount.
- **cron for backups/health checks** — rejected in favor of systemd timers for uniform logging/status with the rest of the host-level tooling.

## Consequences

- The deployment package (`deploy/hermes/`) can be reviewed and iterated on before any real infrastructure exists, at zero infrastructure cost or risk.
- `HERMES-INSTALL-001`'s actual VPS provisioning becomes an execution of an already-reviewed, upstream-verified design, not a from-scratch design-under-pressure exercise.
- This ADR does not select a VPS provider or monthly ceiling — those remain open Owner decisions (`work/BLOCKED.md`), now specifically gating `HERMES-INSTALL-001`.
- No governed document (Master Charter, Constitution, Invariant Kernel) is affected. No secret, credential, or real infrastructure endpoint is introduced by this ADR or its accompanying package.
- Co-locating profiles in one container is now the accepted default, with its real (application-layer only) isolation boundary documented rather than implied — any future profile whose risk profile doesn't fit that boundary gets a dedicated container via a specific, later decision, not a blanket policy change.

## Amendment 1 (post-upstream-audit, first pre-merge review)

An Owner-directed pre-merge audit ("AUDITORÍA PRE-MERGE — HERMES-DEP-001") required checking this design against the real, official `NousResearch/hermes-agent` product rather than assumptions carried over from this repository's own general infrastructure docs. Consulted 2026-07-23 against what was then believed to be release v0.19.0 (2026-07-20) — see "Verified upstream release pin" above for the fuller, independently re-verified confirmation of that same version in Amendment 2. Findings from this first pass, superseded in place where Amendment 2 corrects them further:

- No "worker" process or CLI subcommand exists upstream — removed a fabricated `hermes-worker.service`.
- Docker's own `restart: unless-stopped` (not a custom systemd unit) is the documented supervision mechanism — removed a redundant `hermes-gateway.service`.
- `terminal.backend: docker` reconsidered and reversed to `local` for `ict-trading` (superseded by Amendment 2's fuller justification above, now also applied to `onyx`).
- `terminal.home_mode`'s real values are `auto`/`real`/`profile` — corrected from the invented `profile_scoped`.
- Secret injection redesigned as a three-file model (superseded/restated above with the shared-volume path correction).
- Backups switched to the official `hermes backup` command.
- Documented the `docker` group / `docker exec` privilege trade-off for scheduled backup/health-check jobs.

## Amendment 2 (post-topology-reconciliation, this revision)

A second Owner-directed reconciliation, before any real VPS installation, required re-verifying the exact upstream release (the Owner's own check had surfaced `v0.18.2` as apparently latest — resolved above as a stale/pre-propagation read, not an error in this ADR) and re-checking the deployment topology specifically, which Amendment 1 had not re-examined against the official Docker documentation's own profile-management guidance. That guidance (`docs/user-guide/docker`, consulted 2026-07-23) states plainly: "the recommended deployment is one container hosting all profiles," with a detailed rationale for why the one-container-per-profile pattern this ADR originally chose (and Amendment 1 left unchanged) predates the product's s6-based supervision and is no longer necessary except for specific high-risk-isolation cases. This amendment:

- Corrects the topology to one container, multiple s6-supervised profiles (decision 2, 6, 10 above).
- Adds the verified release pin (tag, commit, digest) in place of the unpinned `nousresearch/hermes-agent:0.19.0` placeholder Amendment 1 had used without independent digest verification.
- Adds the "Real isolation boundaries" table, stating plainly that co-located-profile isolation is application-layer, not OS-layer.
- Adds the "Future dedicated-container option" section as the documented, not-yet-exercised escape hatch for high-risk profiles.
- Confirms `onyx` (not `ict-trading`) as the first profile to be specified for activation, with `ict-trading` remaining a documented future profile, and adds `developer`/`research`/`knowledge`/`blockchain`/`regulation` as further future profiles mapping onto already-specified Brains.
- Changes this ADR's status to **Ratified** (below) — the design is internally consistent: every deliverable in `deploy/hermes/` was updated to match this topology in the same change that introduced this amendment, no profile is activated, no VPS is touched, and the isolation trade-off this correction surfaces is stated rather than hidden.

## Status

**Ratified by Owner for controlled VPS deployment preparation.**

This ratification does not authorize financial execution or unrestricted agent activation. It does not, by itself, authorize connecting to or modifying a real VPS — that remains gated on `HERMES-INSTALL-001` and its own Owner-supplied VPS details (`BACKLOG.md`). No profile has been activated. No credential has been created.
