# Governance Core Schemas

JSON Schema (Draft 2020-12) contracts for the Governance Core, specified but not implemented. See `docs/21_GOVERNANCE_CORE_SPEC.md` onward for the component specifications these schemas support.

- `action-request.schema.json` — what an actor asks Governance to evaluate. Never an execution instruction.
- `policy-decision.schema.json` — the deterministic evaluation output.
- `approval.schema.json` — a Class C approval record through its lifecycle.
- `capability-claims.schema.json` — the logical claims a capability asserts. Never appears on the wire by itself; never contains a secret value or consumption state.
- `capability-protected-header.schema.json` — the decoded JWS Protected Header (`alg`, `kid`, `typ`) a capability is signed under. `alg` is fixed to `Ed25519` (RFC 9864 fully-specified identifier).
- `capability-token.schema.json` — the wire artifact: a JWS Compact Serialization (RFC 7515) string, `{"format": "jws-compact", "token": "protected.payload.signature"}`. Validates surface shape only.
- `audit-event.schema.json` — one append-only, hash-chained audit log entry.
- `kill-switch-event.schema.json` — an emergency-control activation or recovery event.

See `docs/23_CAPABILITY_MODEL.md` for how the three capability contracts relate (Issuance profile, Verification profile) and `docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md` for the cryptographic profile decision.

## Conventions

- All identifiers (`*_id`) are UUID-formatted strings.
- All timestamps are RFC 3339, UTC, `Z` suffix.
- All financial amounts are decimal strings (`^[0-9]+(\.[0-9]+)?$`), never floating-point numbers.
- `correlation_id` is mandatory everywhere and must be identical across a request's action-request, policy-decision, approval, capability claims/token, and audit-event records.
- These schemas define shape only. They do not grant authority, and they do not perform cryptographic verification: an instance validating against `capability-token.schema.json` is not a valid, usable capability unless it was actually issued by Governance under a real policy evaluation and its signature verifies under the Verification profile in `docs/23_CAPABILITY_MODEL.md`.

## Status

Specification only. No Governance API, database, or service reads or writes these schemas yet.

## Validation scope: what "verified" means today

`scripts/verify_foundation.py` and the ad hoc checks performed when this specification was authored perform **structural schema validation**, not full JSON Schema Draft 2020-12 conformance validation. Concretely, what is checked:

- each file parses as valid JSON;
- each file declares `"$schema": "https://json-schema.org/draft/2020-12/schema"`;
- each file the verifier lists is present (existence check, not content check);
- internal `$ref` pointers (`#/$defs/...`) resolve to a location that exists within the same document.

What is **not** checked, and must not be assumed to have been checked:

- full Draft 2020-12 keyword-semantics conformance (e.g. whether every `pattern`, `format`, `if`/`then`/`allOf` combination is itself well-formed per the specification's own meta-schema);
- meta-schema validation (validating each schema document against the official JSON Schema meta-schema);
- that any real instance (an actual action-request, capability, audit event, etc.) validates or fails to validate correctly against these schemas;
- positive and negative test coverage per schema.

"Structural schema validation" is the accurate name for what exists today. Calling it "JSON Schema validation" without qualification overstates the guarantee.

### Future implementation requirement

Before these schemas are relied on by running code, the following must exist (not implemented in this change, no dependency added here):

- a Draft 2020-12-compliant JSON Schema validation library, with a pinned version — **library choice resolved by Owner decision** (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md` — JSON Schema validation library): Python `jsonschema`, `Draft202012Validator`. The exact package version remains to be pinned at implementation time — this ADR decides the library, not the version;
- `check_schema()` run against the official meta-schema for every schema file in this directory (ADR-0011);
- an explicit `FormatChecker` enabled where format keywords (`uuid`, `date-time`) are relied upon for real validation, not just documentation (ADR-0011);
- a positive and negative test suite per schema (at minimum: one instance that should validate, one that should fail validation, per required field and per constraint such as `enum`, `pattern`, and the `audit-event.schema.json` conditional `if`/`then` rules).
