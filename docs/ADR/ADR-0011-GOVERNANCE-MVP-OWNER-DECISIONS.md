# ADR-0011 — Governance MVP Owner Decisions

Status: Ratified
Date: 23 July 2026
Owner: IIOS Owner

## Context

`docs/21_GOVERNANCE_CORE_SPEC.md` through `docs/26_KILL_SWITCH_SPEC.md`, `governance/schemas/README.md`, and ADR-0010 specified the Governance Core's shape and left a defined set of MVP parameters as open questions for the Owner (idempotency window, actor authentication, Class C approval TTL, multiple approvers, capability signing/custody, kill-switch test cadence, Make.com classification, the JSON Schema validation library, and the capability envelope's cryptographic format). This ADR records the Owner's concrete answers to those questions as ratified decisions. It does not alter any architectural boundary fixed by ADR-0010, and it does not authorize implementation — Governance Core remains **specified, not implemented**.

## Decision

### Idempotency

- Default window: **24 hours**.
- Configurable by policy up to a ceiling of **7 days**.
- Key scope: `(actor, action, resource, environment)`.
- A repeated request within the window returns the original decision and does not re-execute the action (`docs/21_GOVERNANCE_CORE_SPEC.md` — Idempotency; closes Open question 1).

### Actor authentication

- **Humans**: OIDC; MFA mandatory; WebAuthn preferred over other second factors.
- **Services, agents, and runtimes**: mTLS with short-lived workload identity. The Owner's personal credentials are never reused for a service/agent/runtime identity.
- A session alone is not sufficient identity — session presence must be paired with the authentication method above, not substituted for it (`docs/21_GOVERNANCE_CORE_SPEC.md` — Authentication; closes Open question 2).

### Class C approvals

- Default TTL: **15 minutes**.
- Maximum TTL: **60 minutes**, and only for reversible actions in non-production environments.
- Expiration forces a fresh approval request; an expired approval is never revivable.
- MVP uses a **single approver** (the Owner).
- `required_approvals > 1` remains supported by the Approval Model's shape (`approval.schema.json`'s `required_approvals`/`decisions[]`) but is **deferred**, not activated, for MVP.
- Self-approval remains prohibited, unchanged from `docs/24_APPROVAL_MODEL.md` (closes Open question 3; partially resolves Open question 4 — multi-approver support is deferred, not decided against, for post-MVP).

### Capability envelope format — corrected 23 July 2026

**This supersedes the original "JWS + EdDSA/Ed25519" wording of this section**, which used the polymorphic JOSE algorithm identifier `EdDSA` and blurred the wire format with the logical claims. The corrected, ratified decision:

```text
JWS Compact Serialization
alg: Ed25519
key type/curve: OKP / Ed25519
kid: mandatory protected-header parameter
typ: iios-capability+jws
```

- **JWS Compact Serialization** (RFC 7515) — `protected.payload.signature`, three Base64URL segments. No JWS Unprotected Header; no JWS JSON Serialization.
- **`alg: "Ed25519"`** — the fully-specified JOSE algorithm identifier for Ed25519 (RFC 9864, which supersedes the polymorphic `EdDSA` identifier for new deployments). **`EdDSA` is excluded for any new capability issuance.**
- Key type/curve: **OKP / Ed25519**.
- **`kid` is a mandatory protected-header parameter** — not an external/unprotected field.
- **`typ: "iios-capability+jws"`** — mandatory protected-header parameter identifying this token type.
- **Single signer during MVP** — one active signing key at a time (see Key custody, unchanged, for the 90-day rotation / 24h overlap window).
- **Both the protected header and the capability claims must be valid I-JSON (RFC 7493) inputs** before RFC 8785 JCS canonicalization: no duplicate property names; Unicode strings preserved exactly with no further normalization; only I-JSON-compatible numbers (no `NaN`, no `Infinity`/`-Infinity`, no non-JSON numeric representation); financial amounts, long numeric identifiers, and any value needing precision a double cannot guarantee are represented as strings, never numbers — including inside `constraints`. An input failing this profile is rejected before signing (`CAPABILITY_CLAIMS_INVALID` or `CAPABILITY_HEADER_INVALID`) and is never issued. Full detail: `docs/23_CAPABILITY_MODEL.md` — "I-JSON profile for JCS." No canonicalizer is implemented by this decision.
- Both the protected header and the claims are canonicalized via **RFC 8785 JCS** before Base64URL encoding and signing (see `docs/23_CAPABILITY_MODEL.md` — Issuance profile, 9 steps). **RFC 7515 does not require JCS or any particular canonicalization** — IIOS adopts it as its own internal deterministic profile for reproducibility, not because JWS mandates it. Verification always operates on the original Signing Input exactly as received; a presented token is never re-canonicalized or re-serialized to check its signature.
- Consumption and revocation state remain server-side, keyed by `capability_id`, never part of the signed structure (unchanged from the original decision).
- **No downgrade or dynamic algorithm selection is permitted.** The verifier uses an exact allowlist containing exactly one algorithm: `Ed25519`. A token presenting any other `alg` value — including `EdDSA` — is rejected (`CAPABILITY_ALGORITHM_DENIED`), not accepted as a legacy fallback.
- **Read compatibility with older tokens does not apply for MVP**, because no capability has been issued yet — there is no legacy population to remain compatible with.
- No bespoke/proprietary cryptographic format, no raw JSON payload sitting next to a detached signature as the wire representation, and no `algorithm`/`key_id` as external unprotected fields — all superseded by the JWS Compact Serialization profile above (closes `docs/23_CAPABILITY_MODEL.md` Open question 1, and `docs/21_GOVERNANCE_CORE_SPEC.md` Open question 5's format half).

Concrete claims/header/wire contracts: `governance/schemas/capability-claims.schema.json`, `governance/schemas/capability-protected-header.schema.json`, `governance/schemas/capability-token.schema.json` (redefined; see `docs/23_CAPABILITY_MODEL.md`).

### Key custody

- Private signing key held in **KMS, HSM, or an external Vault** — never in the repository, never in Markdown, never in an environment variable forwarded to a sandbox or agent runtime.
- **Non-exportable** where the provider supports it.
- Public key distributed via a **trusted registry / JWKS** endpoint.
- **Rotation every 90 days.**
- Maximum overlap window for a previous key remaining valid for verification: **24 hours** after a new key is published.
- (Closes `docs/23_CAPABILITY_MODEL.md` Open question 2, and the custody half of `docs/21_GOVERNANCE_CORE_SPEC.md` Open question 5.)

### Capability TTLs by class

| Class | Maximum TTL when a capability is required | `max_uses` default |
|---|---|---|
| A | 10 minutes | — (not specified here; per-rule, see `docs/22_POLICY_ENGINE_EVALUATION.md`) |
| B | 5 minutes | 1 |
| C | 2 minutes | 1 |
| D | Never issued | n/a |

(Refines `docs/23_CAPABILITY_MODEL.md` Open question 3 with concrete ceilings; the exact Class A `max_uses` for read-mostly reusable cases remains governed by the issuing policy rule, not fixed to 1 here, consistent with `docs/23_CAPABILITY_MODEL.md`'s existing "values above 1 require explicit policy justification" rule.)

### Rate limiting

Capability issuance rate limiting is **independent of** model-cost budgets and tool/cost limits (`docs/12_COST_GOVERNANCE.md`) — a separate control, not a reuse of the cost caps.

Initial configurable values, per `subject`:

| Class | Limit |
|---|---|
| A | 60 requests/minute |
| B | 10 requests/minute |
| C | 5 requests/hour |
| D | 0 |

(Closes `docs/23_CAPABILITY_MODEL.md` Open question 4.)

### `audience`

Single-valued for MVP: one capability authorizes exactly one executor. Multiple valid executors per capability is deferred (closes `docs/23_CAPABILITY_MODEL.md` Open question 5).

### Secrets

Restates and ratifies, without modification, the verb split already specified in `docs/21_GOVERNANCE_CORE_SPEC.md` — "Secret handling: value vs. reference":

- `secret_value.read` is always prohibited for models and agents, unconditionally.
- `secret_reference.use` is Class C.
- Secret Manager delivers the secret directly to the authorized process, never through a model's context.
- A model or agent receives only status, result, or a redacted reference — never the value.

No change to `docs/21_GOVERNANCE_CORE_SPEC.md`'s existing text is required; this ADR confirms it as Owner-ratified rather than proposed.

### Make.com

- Listing or querying scenario metadata **may** be Class A, and only through a connector that is technically read-only and allowlisted.
- Executing, activating, deactivating, editing, or creating a scenario is **Class C**.
- **No new subclass is created for MVP.**

This resolves case #14 in the 20-case matrix (`docs/21_GOVERNANCE_CORE_SPEC.md`) concretely: the read-only metadata path is now a defined Class A case (subject to a real allowlisted connector existing, which is not implemented here), and every mutating Make.com action is Class C, consistent with ADR-0008's Cowork write-connector boundary. Closes `docs/21_GOVERNANCE_CORE_SPEC.md` Open question 7.

### Kill Switch test cadence

- **L1, L2**: monthly drill, staging.
- **L3**: quarterly drill, staging.
- **L4**: semiannual drill in staging, plus an annual tabletop exercise for production.
- **L5**: annual tabletop exercise.
- A **real L5 activation drill** (not a tabletop) requires **separate, explicit Owner authorization**, independent of the standing cadence above — the cadence authorizes tabletop/staging drills, not a live L5 test.

(Closes `docs/21_GOVERNANCE_CORE_SPEC.md` Open question 6 / `docs/26_KILL_SWITCH_SPEC.md`'s proposed cadence.)

### JSON Schema validation library

- Python `jsonschema` library.
- `Draft202012Validator`.
- Exact package version to be pinned **at implementation time** (not pinned by this ADR).
- `check_schema()` run against the official meta-schema for every schema file.
- Explicit `FormatChecker` enabled where format keywords (`uuid`, `date-time`) are relied upon for real validation, not just documentation.
- Positive and negative test coverage required per schema, per the existing requirement in `governance/schemas/README.md`.

This decides the *library and validation approach*; it does not itself constitute implementation, and no dependency is added by this ADR (partially closes `governance/schemas/README.md`'s "Future implementation requirement" — the choice is now decided, the pinned version and actual installation remain implementation-time work).

### Policy Engine

Ratifies, without altering, the MVP recommendation and mandatory conditions already specified in `docs/22_POLICY_ENGINE_EVALUATION.md`:

- Closed, declarative JSON rules for MVP.
- No scripts or arbitrary code.
- Operators via an explicit allowlist.
- Deterministic evaluation order and precedence.
- Conflict resolves to deny or the more restrictive class.
- Policy bundle is versioned and checksum-protected, mirroring the Invariant Kernel's manifest pattern.
- This is a **reversible** decision: future migration to Cedar or OPA remains possible after evaluation, not foreclosed by this ratification.

No new text is required in `docs/22_POLICY_ENGINE_EVALUATION.md`; this ADR confirms its existing "Recommendation for MVP" and "Mandatory conditions" sections as Owner-ratified.

## Alternatives considered and discarded

- **PASETO instead of JWS** for the capability envelope: discarded per Owner decision in favor of JWS Compact Serialization with `alg: Ed25519`, which has broader library support and existing key-management tooling (KMS/HSM/JWKS) to pair with the chosen custody model.
- **`alg: "EdDSA"`** (the polymorphic JOSE identifier): discarded in favor of the fully-specified `alg: "Ed25519"` per RFC 9864, which removes algorithm ambiguity at the verifier — `EdDSA` alone does not pin the curve, and a verifier accepting it must carry extra logic to also pin the curve out-of-band. Excluding it entirely from new issuance removes that class of downgrade/confusion risk.
- **A flat envelope with `algorithm`/`key_id` as external unprotected fields and a raw JSON payload beside a detached signature**: discarded — this was the original schema shape and is not a real JWS serialization; it left `alg`/`kid` unauthenticated (outside the signed protected header) and made the wire artifact ambiguous with the logical claims view. Replaced by the three-contract split (claims / protected header / wire token) below.
- **No idempotency ceiling** (unbounded configurable window): discarded — an unbounded window makes stale-decision replay risk unbounded too; 7 days caps it while still accommodating realistic retry/backoff scenarios.
- **Multiple approvers for MVP**: discarded for now — adds coordination overhead with only one Owner currently operating the system; the model supports it for when a second approver role exists.
- **A new Make.com "read-only automation" subclass**: discarded — the existing Class A action path already covers it once a real read-only allowlisted connector exists; a new subclass would duplicate machinery for no additional safety.

## Consequences

These parameters give implementers concrete numbers instead of ranges, removing a class of ambiguity that would otherwise be resolved ad hoc during a future implementation phase, possibly under time pressure. They also create commitments that a future implementation must actually meet (e.g. 90-day key rotation, monthly L1/L2 drills) — operational discipline this ADR creates an expectation for, not code that enforces it yet.

## Security/financial impact

None directly — still no service, credential, or financial capability exists. The impact is entirely on the *quality* of a future implementation's security posture: fixing short capability TTLs, mandatory MFA/mTLS, external key custody, and a real drill cadence before any code exists reduces the chance that these get relaxed under later implementation pressure.

## Evidence

- `docs/21_GOVERNANCE_CORE_SPEC.md`, `docs/23_CAPABILITY_MODEL.md`, `docs/24_APPROVAL_MODEL.md`, `docs/26_KILL_SWITCH_SPEC.md`, `governance/schemas/README.md` — updated with pointers to this ADR for each closed question, per the delivery report.
- `docs/22_POLICY_ENGINE_EVALUATION.md` — unchanged; ratified as-is.
- `python scripts/verify_invariant_kernel.py` and `python scripts/verify_foundation.py` — pass unchanged; `invariants.json`, Charter, and Constitution untouched by this change.

## Rollback/review date

Rollback: revert this branch before merge; no schema, Charter, Constitution, or Invariant Kernel file is touched, so rollback is a clean branch discard.
Review date: before Governance Core implementation begins (these are exactly the parameters an implementer needs first), and at the JSON Schema library's version-pinning decision, which remains open.
