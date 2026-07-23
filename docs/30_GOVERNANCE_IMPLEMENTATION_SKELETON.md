# IIOS Governance Core — Implementation Skeleton

**Status:** In review (`GOV-IMP-001`)
**Authorization:** Owner instruction, "AUTORIZACIÓN DEL OWNER — PHASE 3" (23 July 2026), scoped explicitly to a local, deterministic, in-memory reference implementation — not production.
**Parent specification:** `docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`, ADR-0010, ADR-0011, ADR-0012 (Proposed)

```text
Governance Core implementation skeleton: in review
Governance Core production implementation: not started
```

## Purpose

Prove the ratified specification is actually implementable, deterministic, and testable — `action-request → schema validation → deterministic classification → Kernel evaluation → policy evaluation → approval requirement → capability requirement → decision → audit event` — with real code, real tests, and no external dependencies. **Governance decides. Governance never executes an external action.** There is no method anywhere in this package that calls out to a trading platform, a database, a filesystem outside `governance/`, or any network endpoint.

## Structure

```text
src/iios_governance/
  domain/          — pure logic: models, action_classifier, policy_engine,
                     approval_service, capability_service, audit_chain,
                     kill_switch, reason_codes, errors. No I/O.
  application/      — orchestration: decision_pipeline (pure), governance_service
                     (wires ports together, the only place with I/O side effects
                     beyond reads).
  ports/            — Protocols: clock, canonicalizer, audit_store, approval_store,
                     capability_store, policy_repository, kernel_repository,
                     idempotency_store, budget_tracker, signature_verifier.
  adapters/
    memory/         — in-memory implementations of every port except Kernel/
                     policy loading (production-shaped, test- and skeleton-safe).
    filesystem/     — loads and checksum-verifies the REAL governance/invariant-kernel/
                     and governance/policy-bundles/ from disk. Read-only.
    system_clock.py — the only production Clock; never imported by tests.

tests/governance/    — pytest suite, 133 tests, no network calls, no real-time
                     dependency (every test uses an injectable FixedClock).
```

Two ports named in the original suggested tree turned out to need
extension: `idempotency_store.py` and `budget_tracker.py` were added
because the mandatory "duplicate request" and "budget exceeded" test
cases require them, and `signature_verifier.py` was added because
capability verification needs a pluggable place to NOT do real
cryptography (see below). `adapters/filesystem/` was added because the
Kernel and MVP policy bundle must be loaded from real, checksum-verified
files on disk — an in-memory-only adapter would defeat the point of
checksum verification.

## Evaluation flow

`GovernanceService.evaluate(action_request_dict) -> PolicyDecision`:

1. Validate against `governance/schemas/action-request.schema.json`. Invalid → `SCHEMA_INVALID` deny, never an unhandled exception.
2. Idempotency check (`actor:verb:resource:environment:idempotency_key`) — a repeat within the cache returns the original decision, `replayed=True`.
3. Load and checksum-verify the Invariant Kernel (`adapters/filesystem/filesystem_kernel_repository.py`, same canonical-hash algorithm as `scripts/verify_invariant_kernel.py`).
4. Check the Kill Switch for the requesting actor's scope.
5. Check the budget scope (`domain:profile:task_id`).
6. Load and checksum-verify the active policy bundle (`governance/policy-bundles/mvp/`).
7. Per item: `domain/action_classifier.py` classifies deterministically (never consulting `classifier_hint`); `domain/policy_engine.py` checks the Kernel invariants first (short-circuits on match), then the policy bundle rules (deny-by-default, exact-match-beats-wildcard, stricter-effect-wins-ties).
8. `require_approval` outcomes create a real `pending` Approval via `domain/approval_service.py`.
9. Two audit events (`request_received`, `policy_decision`) are appended to the hash chain. If the audit write fails and the decision was `allow`/`require_approval`, the decision is overridden to `deny` (`AUDIT_UNAVAILABLE`) — no allow is ever granted without a successful audit write.
10. The decision is cached under the idempotency key and returned.

## Components — functional (real logic, real tests, in-memory or filesystem-backed)

- Invariant Kernel loader — loads and checksum-verifies the **real, ratified** Kernel.
- Action Request schema validation — Draft 2020-12, `jsonschema==4.26.0`.
- Deterministic Action Classifier — pure function, no LLM, no hint.
- Policy Engine — loads and checksum-verifies a **real** MVP policy bundle (`governance/policy-bundles/mvp/`, format defined in ADR-0012, Proposed); deny-by-default; precedence/specificity resolution.
- Approval state machine — all seven states, structural self-approval rejection, TTL expiry, single-consumption.
- Capability contracts — claims/header schema validation, I-JSON parsing (rejects duplicate keys, `NaN`/`Infinity`), wire-token surface-shape validation, the full 8-step consumption pipeline, server-side revocation/replay tracking.
- Audit hash chain — genesis sentinel, `previous_event_hash` linkage, tamper detection via chain re-verification.
- Kill Switch — L1–L5, Owner-grade-auth-only activation/recovery, scope-matched blocking, standalone (no Orchestrator dependency).
- Fail-closed behavior — Kernel unavailable/mismatched, policy bundle unavailable/invalid, Governance unavailable, audit unavailable, kill switch active, budget exceeded, ambiguous classification: all verified by dedicated tests.

## Components — simulated (test-only, never imported from `src/`)

- **`tests/governance/fakes.py::FakeSigner` / `FakeSignatureVerifier`** — HMAC-SHA256 over a hardcoded test-only string, standing in for Ed25519. Lets the full capability consumption pipeline (header/claims validation, replay, expiry, revocation, audience/resource matching) be tested end-to-end without any real key material.
- **`tests/governance/fakes.py::DeterministicTestCanonicalizer`** — sorted-keys, compact-separator JSON serialization. **Not RFC 8785 JCS.** Deterministic enough to test hash-chain linkage and tamper detection, but explicitly not a conformance claim.

## Components — not implemented (production wiring fails closed)

- **`domain/capability_service.py::DisabledSignatureVerifier`** — the only signature verifier ever wired into `GovernanceService` in this skeleton. Raises `CryptoNotImplementedError` → `CAPABILITY_CRYPTO_NOT_IMPLEMENTED` on every call. No Ed25519 library is imported anywhere in `src/`.
- **RFC 8785 JCS canonicalizer** — `ports/canonicalizer.py` has no production adapter. No independently-maintained, verifiable Python JCS implementation was adopted in this task (see "Open question" below); the port exists so a real one can be plugged in later without touching `domain/audit_chain.py`.
- **KMS/HSM/Vault** — no key custody of any kind. No key is generated, stored, or referenced anywhere in this codebase.
- **PostgreSQL/Supabase, Redis** — every store is `adapters/memory/*`, process-local, lost on restart. Production persistence is future work.
- **HTTP transport / FastAPI** — `GovernanceService.evaluate()` is a plain Python method. No endpoint, no server, no network listener exists.
- **Hermes, Brains, Agents, Graphify, Obsidian, MetaApi, Make.com, MCP connectors, Control Center** — none referenced by any import in `src/`.

## Security boundaries

- No secret value is ever constructed, stored, or logged by this package.
- `CapabilityService` never trusts a client's claim about remaining uses — `uses_remaining` and `revoked` live only in `CapabilityServerState`, server-side.
- Self-approval is rejected structurally in `ApprovalService.decide()` (`approver_id == requested_by` → `SelfApprovalError`), independent of and in addition to the JSON Schema `$comment`-only documentation in `governance/schemas/approval.schema.json`.
- The Kill Switch's `activate`/`recover` reject any `auth_method` other than `owner_session`, `owner_out_of_band`, or `delegated_token` — an Orchestrator or runtime actor cannot activate or recover any level.
- `governance/policy-bundles/mvp/` is checksum-protected exactly like the Invariant Kernel; `PreToolUse` guard coverage for this new path is a follow-up item (not yet added to `.claude/hooks/pretool_guard.py` — see Next steps).

## Running the tests locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src tests
python -m pytest tests/governance --cov=iios_governance --cov-report=term-missing
```

`.venv/` is git-ignored; nothing about running these commands touches any file outside this repository.

## Pinned dependencies and their source

| Package | Version | Purpose |
|---|---|---|
| `jsonschema` | `4.26.0` | Draft 2020-12 validation (`Draft202012Validator`), resolved and installed during this task |
| `pytest` | `9.1.1` | Test runner |
| `pytest-cov` | `7.1.0` | Coverage report |
| `ruff` | `0.15.22` | Lint + format |
| `mypy` | `2.3.0` | Type checking |
| `types-jsonschema` | `4.26.0.20260518` | Type stubs for `jsonschema`, matched to the runtime version |

All versions were resolved from the live package index during this task (not guessed) and are pinned exactly in `pyproject.toml`.

## Open questions / next steps

1. **RFC 8785 JCS library selection** — needs a security-reviewed, independently-maintained package before the audit chain or capability issuance can move past this skeleton. Not resolved in this task.
2. **Ed25519 signing/verification library and key custody** — same status; `DisabledSignatureVerifier` remains the only production wiring until this is resolved (ADR-0011, `docs/23_CAPABILITY_MODEL.md` Open questions).
3. **ADR-0012 (policy bundle format) is Proposed, not Ratified** — the skeleton's tests and code work against it; formal ratification is a separate Owner decision.
4. **`PreToolUse` guard** (`.claude/hooks/pretool_guard.py`) does not yet protect `governance/policy-bundles/` the way it protects `governance/invariant-kernel/` — a follow-up task, not done here.
5. **Persistence** — every adapter is in-memory; a real implementation phase needs PostgreSQL/Supabase-backed adapters implementing the same ports, which is exactly why the ports/adapters split exists.
