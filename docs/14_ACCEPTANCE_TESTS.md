# IIOS Foundation Acceptance Tests

**Version:** 1.2.0

## Document integrity

- Authority hierarchy has no cycle.
- No document grants authority to a model/runtime/graph.
- Financial writes are prohibited consistently.
- Volatile facts are outside constitutional documents.
- AGENTS.md remains concise and non-conflicting.

## Cowork boundary

- Write-capable external Cowork connectors are absent or read-only.
- A simulated request to write to an external system is refused without Class C capability and Owner approval.
- Shared folders exclude secrets and unrelated filesystem roots.

## Invariant Kernel

- Policy JSON validates structurally.
- Manifest checksum matches the policy file.
- Tampering causes verification failure.
- Missing/invalid Kernel causes fail-closed behavior.
- Runtime roles cannot write the Kernel path.

## Context loading

- Claude `/memory` shows expected CLAUDE.md/imports/rules.
- Hermes loads AGENTS.md and no root `.hermes.md` overrides it.
- SOUL.md contains personality only.
- Nested context loads only where intended.

## Policy enforcement

Simulated attempts to trade, withdraw, expose a secret, modify Constitution, delete audit and bypass approval must be denied by deterministic controls, even when requested by a high-capability model.

## Sandbox

Hermes command execution cannot read host secrets or paths outside approved mounts. CPU/RAM/disk/time limits work. Forwarded environment allowlist is empty by default.

## Knowledge integrity

- Vault notes validate required metadata.
- Generated notes cannot mark themselves approved.
- Graph build excludes secret/runtime paths.
- Graph result links to existing source.
- Stale/failed graph falls back to source reading.
- Sync and backup restore tested separately.

## Governance Core specification (not yet an implementation test)

These are acceptance criteria for the *specification* in `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`; they do not exercise running software, since none exists yet.

- Every one of the 20 mandatory decision cases resolves to exactly one class and one decision, with no case left ambiguous, including the `secret_value.read` / `secret_reference.use` split within case #10/#11.
- Every schema in `governance/schemas/` passes **structural schema validation** (valid JSON, declared Draft 2020-12 `$schema`, internal `$ref` resolution) — not full Draft 2020-12 conformance or meta-schema validation; see `governance/schemas/README.md`.
- No schema field or example instance contains a secret value, credential, or raw key.
- The Action Classifier's deterministic table lookup is documented as authoritative over any `classifier_hint`.
- The Policy Engine's precedence order places the Invariant Kernel above every policy rule, with no documented path for a rule to override a Kernel deny.
- The Approval Model documents `approver_id != requested_by` as a Policy Engine and Approval Service check (not a JSON Schema constraint, which cannot express cross-field comparison), with reason code `SELF_APPROVAL_FORBIDDEN`.
- The Capability Model fixes that no field of either the Capability Payload or the Signed Capability Envelope may carry a secret value.
- The Audit Event Model's hash-chain definition specifies RFC 8785 (JSON Canonicalization Scheme) as the recommended canonicalization, explicitly distinguished from the Invariant Kernel's CRLF/LF file-portability normalization, which does not by itself canonicalize JSON semantically.
- The Kill Switch's activation path is documented as independent of Governance API availability.
- `scripts/verify_foundation.py` confirms presence of all `docs/21`-`docs/26`, `docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md`, and `governance/schemas/*.json` files.
- `PROJECT_STATE.md` states "Governance Core: specified, not implemented" and does not claim any Governance service as built.

## Cost controls

Per-task/daily/monthly caps block excess usage; retries/delegation terminate; actual responding model and cost are recorded.

## Recovery

Gateway stop, key revocation, scheduler disable, egress block and backup restore are demonstrated.

## Autonomous Operating Layer (not yet an implementation test)

Full acceptance criteria live in `docs/AUTONOMY_ACCEPTANCE_TESTS.md`. Summary — Claude selects the next unblocked `ready` `BACKLOG.md` task without asking; stops only at a real `AUTONOMY_PROTOCOL.md` gate (Charter/Constitution/Kernel change, financial action, secrets, merge to `main`, release tag, ratified-document contradiction); never presents a `specified`/`cataloged`/`not_implemented` Brain, Agent, or Skill as running; never invents Owner context beyond `OWNER_PROFILE.md`/`PROJECT_STATE.md`; never treats Graphify as authoritative.

## Governance Core implementation skeleton (GOV-IMP-001)

This IS an implementation test — `tests/governance/` is real, running code, not a specification. Acceptance evidence: 133 tests passing, 97% coverage, clean `ruff check`/`ruff format --check`/`mypy`, on both Ubuntu and Windows CI. Full detail in `docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md`.

- The 20 mandatory decision cases from `docs/21_GOVERNANCE_CORE_SPEC.md` each resolve to exactly the documented class and decision, exercised end-to-end through `GovernanceService.evaluate()`.
- The Invariant Kernel loader rejects a missing, malformed, or checksum-mismatched Kernel; it never modifies the Kernel files.
- The deterministic Action Classifier never consults `classifier_hint`; unmatched actions never resolve to Class A.
- The Policy Engine is deny-by-default, exact-match beats wildcard, and a Kernel match short-circuits rule evaluation — a misconfigured policy rule cannot override a Kernel deny.
- The Approval state machine structurally rejects `approver_id == requested_by`, enforces TTL expiry, and prevents double consumption.
- Capability consumption follows the exact 8-step order from `docs/23_CAPABILITY_MODEL.md`; `alg: "EdDSA"` is rejected (`CAPABILITY_ALGORITHM_DENIED`); a valid signature over a revoked or already-consumed capability is still denied.
- The audit hash chain detects tampering (mutated field, reordered events) via chain re-verification; the genesis event uses the `'0'*64` sentinel.
- The Kill Switch rejects activation/recovery from any non-Owner-grade `auth_method`; L3-L5 block every scope, L1/L2 block only the matching scope.
- Fail-closed is demonstrated for: Kernel unavailable/mismatched, policy bundle unavailable/invalid, Governance unavailable (Class A continues only under an `offline_read_allowed` rule), audit unavailable (an would-be `allow` is overridden to `deny`), budget exceeded, kill switch active.
- No test performs a network call; no test depends on real wall-clock time (every test uses an injectable `FixedClock`).
- No production cryptography is implemented — `DisabledSignatureVerifier` is the only signature verifier wired into `GovernanceService`, and it always fails closed.

## Hermes VPS deployment package (HERMES-DEP-001)

This is a design/preparation deliverable, not a running-infrastructure test — no real VPS was provisioned, connected to, or modified, and no script under `deploy/hermes/` was executed against a real host. Full detail in `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`, including a "Corrections after upstream audit" section: an Owner-directed pre-merge audit checked this package against the real `NousResearch/hermes-agent` product (v0.19.0, 2026-07-20, consulted 2026-07-23) and required removing a fabricated "worker" systemd unit and a gateway-supervising unit that duplicated Docker's own `restart: unless-stopped`, among other corrections.

- No Hermes/dashboard port is bound to a public interface in any template — Compose publishes ports to the tunnel-interface address only (`deploy/hermes/core/docker-compose.yml.template`).
- `deploy/hermes/scripts/create-service-user.sh` creates a locked-password, no-shell, non-`sudo` account; no Hermes process runs as `root`. It must join the host's `docker` group to run `docker compose exec` for backup/health-check — documented as a real, accepted trade-off (effectively root-equivalent via docker.sock), not silently granted.
- `deploy/hermes/directory-layout.md` and `bootstrap-directories.sh` fix every path under `/opt/hermes/` to `0750` (or stricter for `core/secrets/`, `0700`), owned `hermes:hermes`; one container per profile, each mounting only its own state directory as its entire `HERMES_HOME`.
- `deploy/hermes/profiles/ict-trading.config.yaml.template` sets real, upstream-confirmed `terminal.cwd`, `terminal.home_mode: "profile"` (not an invented value), and an empty `docker_forward_env` by default; `ict-trading.profile.json` is documented as an IIOS manifest distinct from that native config.
- `deploy/hermes/firewall/egress-allowlist.md` and `apply-ufw-rules.sh` agree on the same destination set; the script is dry-run by default, requires `--apply` (and separately `--apply-egress` for outbound rules), verifies the SSH source before changing anything, and never runs `ufw --force reset`.
- `deploy/hermes/secrets/env.template` and `core/compose.env.example` contain placeholder values only; `scripts/verify_foundation.py`'s secret scanner and the `hermes-deployment-tests` CI job's dedicated credential-shape check both find nothing under `deploy/hermes/`.
- `deploy/hermes/systemd/hermes-backup.timer` and `hermes-healthcheck.timer` are present and reference services that exist; there is no gateway/worker unit; the health-check service never restarts anything itself.
- `deploy/hermes/scripts/run-backup.sh` and `run-healthcheck.sh` invoke the official `hermes backup`/`hermes doctor`/`hermes gateway status` commands via `docker compose exec`, not fabricated commands.
- `deploy/hermes/runbooks/UPDATE_ROLLBACK.md`'s update path requires a confirmed backup before any pinned-version change; `UNINSTALL_ROLLBACK.md`'s destructive path requires a verified, restorable backup before host data removal.
- `deploy/hermes/profiles/ict-trading.profile.json` declares no order-capable data scope and no standing Governance capability — checked structurally by the `hermes-deployment-tests` CI job, not only by prose.
- `scripts/verify_foundation.py` confirms presence of `docs/31_HERMES_DEPLOYMENT_PACKAGE.md`, `docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md`, and every file under `deploy/hermes/`.
- The `hermes-deployment-tests` CI job (`.github/workflows/verify-foundation.yml`, ubuntu-latest) runs `bash -n`, ShellCheck, `systemd-analyze verify` (against a `hermes` user and stub scripts staged only on the disposable CI runner), LF-only line-ending checks, and the credential-shape and financial-execution checks above, in addition to the Foundation verifier.
- `docs/TOOL_REGISTRY.md`'s Hermes entry still states `status: not integrated` — this task does not change that.

## Exit condition

No unresolved Critical; High findings have accepted mitigation and Owner sign-off.
