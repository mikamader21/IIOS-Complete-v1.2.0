# Governance Core Schemas

JSON Schema (Draft 2020-12) contracts for the Governance Core, specified but not implemented. See `docs/21_GOVERNANCE_CORE_SPEC.md` onward for the component specifications these schemas support.

- `action-request.schema.json` — what an actor asks Governance to evaluate. Never an execution instruction.
- `policy-decision.schema.json` — the deterministic evaluation output.
- `approval.schema.json` — a Class C approval record through its lifecycle.
- `capability-token.schema.json` — a Signed Capability Envelope wrapping a short-lived, scoped Capability Payload. Never contains a secret value.
- `audit-event.schema.json` — one append-only, hash-chained audit log entry.
- `kill-switch-event.schema.json` — an emergency-control activation or recovery event.

## Conventions

- All identifiers (`*_id`) are UUID-formatted strings.
- All timestamps are RFC 3339, UTC, `Z` suffix.
- All financial amounts are decimal strings (`^[0-9]+(\.[0-9]+)?$`), never floating-point numbers.
- `correlation_id` is mandatory everywhere and must be identical across a request's action-request, policy-decision, approval, capability-token and audit-event records.
- These schemas define shape only. They do not grant authority: an instance validating against `capability-token.schema.json` is not a valid capability unless it was actually issued by Governance under a real policy evaluation.

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

- a Draft 2020-12-compliant JSON Schema validation library, with a pinned version;
- meta-schema validation of every schema file in this directory against the official JSON Schema meta-schema;
- a positive and negative test suite per schema (at minimum: one instance that should validate, one that should fail validation, per required field and per constraint such as `enum`, `pattern`, and the `audit-event.schema.json` conditional `if`/`then` rules).
