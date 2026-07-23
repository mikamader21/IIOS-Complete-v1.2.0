# IIOS Audit Event Model

**Version:** 0.1.0
**Status:** Specified, not implemented
**Parent:** `docs/21_GOVERNANCE_CORE_SPEC.md`
**Schema:** `governance/schemas/audit-event.schema.json`

## Purpose

An append-only, tamper-evident record of everything Governance decided and everything the Orchestrator executed under a capability. Audit Authority is independent of the Orchestrator (ADR-0009): it receives evidence, it does not command execution, and execution roles cannot delete or rewrite it (Constitution Article III.2).

## Append-only hash chain

### Why the Invariant Kernel's LF normalization does not apply here

`scripts/verify_invariant_kernel.py` (v1.2.1) normalizes CRLF/CR to LF before hashing `invariants.json`. That fix solves one specific problem: a **versioned text file** checked out on different operating systems must hash identically regardless of the checkout tool's line-ending behavior. An audit event is not a checked-out file — it is a **JSON value** produced programmatically, potentially by different languages, libraries, or serializers over the system's lifetime. Two serializers can produce byte-for-byte different, equally valid JSON for the same logical value: different key order, different whitespace, different number formatting (`1.0` vs `1`), different escaping. Line-ending normalization says nothing about any of that. Presenting the Kernel's fix as sufficient for audit-event hashing would be incorrect and is corrected here: **CRLF/LF normalization resolves versioned-file portability; it is not semantic JSON canonicalization**, and the two problems require different, non-overlapping solutions.

### Recommended design: RFC 8785 (JSON Canonicalization Scheme)

For the audit hash chain, the recommended canonicalization is **RFC 8785 — JSON Canonicalization Scheme (JCS)**, adopted as a design decision, **not implemented in this change** (no library is added; see `docs/22_POLICY_ENGINE_EVALUATION.md`-style "specified, not installed" posture). JCS defines, precisely and interoperably:

- **Canonical UTF-8 serialization**: the event is serialized as UTF-8 text with no byte-order mark, matching RFC 8785 §3.2's encoding rules.
- **Deterministic property ordering**: object member names are ordered by their UTF-16 code unit sequence (RFC 8785 §3.2.3), so any two conformant implementations produce identical output for the same logical value, independent of insertion order or language/library defaults.
- **Normalized JSON representation**: RFC 8785 fixes number formatting (via the ECMAScript `Number::toString` algorithm), string escaping, and whitespace elimination, closing exactly the gap that line-ending normalization does not address.

### What is signed/hashed, and what is not

- `event_hash` is computed over the JCS-canonicalized form of **every field except `event_hash` itself**. `event_hash` cannot be part of its own input.
- `previous_event_hash` **is included** in the material that is hashed — this is what makes the chain a chain: each event's hash is a function of the prior event's hash, not just of the current event's own fields.
- `event_hash = SHA-256(JCS(event_with_event_hash_field_omitted))`, using the hex-lowercase digest already used elsewhere in this project (`governance/invariant-kernel/manifest.json` pattern).

### Genesis event

The first event in a chain (or chain partition) sets `previous_event_hash` to 64 `'0'` characters — an explicit, schema-checkable sentinel (`audit-event.schema.json` already constrains this via `pattern: "^(0{64}|[a-f0-9]{64})$"`), not `null` or an omitted field, so "this is a genesis event" is a distinguishable, verifiable claim rather than an absence of data.

### Chain verification procedure

To verify a stored chain (or a chain segment) is untampered:

1. Start from the known genesis event (`previous_event_hash == '0'*64`) or from a prior externally-attested checkpoint hash.
2. For each event in append order: recompute `SHA-256(JCS(event_with_event_hash_omitted))` and confirm it equals the stored `event_hash`.
3. Confirm the next event's `previous_event_hash` equals the current event's `event_hash`.
4. Any mismatch at step 2 or 3 identifies the exact event where the chain broke — either that event was altered, or an event was inserted/removed/reordered relative to what was originally appended.

This procedure is a specification for a future verifier (analogous in spirit to `scripts/verify_invariant_kernel.py`), not implemented in this change.

### Integrity today vs. tamper resistance tomorrow

SHA-256 hash-chaining (as specified here) gives **tamper-evidence**: a party with read access to the full chain can detect retroactive edits. It does **not**, by itself, give **tamper-resistance against an actor who controls the storage and can rewrite the entire chain consistently** (recomputing every subsequent hash after an edit). That stronger guarantee requires one of:

- an external, periodic **signature** over checkpoint hashes by a key the storage-owning role does not control, or
- **anchoring** checkpoint hashes to an append-only system outside the audit store's own control (e.g. a separate, more restricted logging sink, or an external timestamping service).

Neither is designed or implemented in this change. It is recorded here as a known future hardening step, to be addressed by its own ADR and security review before Governance Core moves toward production, not assumed away by the hash chain alone.

Chains are scoped per `correlation_id` for readability but the underlying hash linkage may also run globally per audit partition; the exact partitioning strategy is an implementation decision deferred to the build phase. What is fixed now: no partitioning strategy may make an event's prior linkage optional.

## Fields

See `governance/schemas/audit-event.schema.json` for the normative shape and the conditional `required` rules already encoded there (`if event_type == X then require Y`). Full field list:

```text
event_id, event_type, timestamp, actor, request_id, correlation_id,
action_class, policy_version, decision, reason_codes, approval_id,
capability_id, tool, resource, result, cost, evidence,
previous_event_hash, event_hash
```

## Required fields by event type

| `event_type` | Always required (beyond the base set) | Notes |
|---|---|---|
| `request_received` | — | First event in a request's lifecycle |
| `policy_decision` | `policy_version`, `decision`, `reason_codes` | One per evaluation, including replays (`replayed` noted in the referenced `policy-decision`, not duplicated here) |
| `approval_requested` / `approval_decided` / `approval_expired` / `approval_revoked` | `approval_id` | One event per state transition, not one event for the whole lifecycle |
| `capability_issued` / `capability_consumed` / `capability_revoked` | `capability_id` | `capability_consumed` is emitted even for a failed consumption attempt (`result: blocked`) |
| `execution_result` | `result`, `tool`, `resource` | Emitted by the Orchestrator/executor, referencing the `capability_id` used |
| `budget_exceeded` | `cost` | Emitted once per scope crossing, not per subsequently blocked request |
| `governance_unavailable` | — | `actor` is `system:governance`; queued locally if a local queue is reachable |
| `audit_unavailable` | — | Emitted by the calling component's own local fallback path, if any exists; if not, the blocking decision itself is the only trace, per the fail-closed rule that no execution proceeds without an audit path |
| `kill_switch_activated` / `kill_switch_recovered` | — | Cross-referenced with `governance/schemas/kill-switch-event.schema.json`; the audit event records that it happened, the kill-switch-event record is the operational detail |
| `kernel_integrity_violation` | `reason_codes` | Mirrors a `verify_invariant_kernel.py`-style checksum mismatch detected at runtime, not just at CI |

## What audit events never contain

Secret values, raw credentials, full request/response bodies containing sensitive data, or personally identifying information beyond what the actor model already requires. `evidence` holds pointers (object storage keys, `decision_id` references), never the sensitive payload itself — this mirrors the `secret_reference.use` case (`docs/21_GOVERNANCE_CORE_SPEC.md` case #10/#11, "Secret handling: value vs. reference"), where the audit trail proves a scoped use happened without ever holding the secret's value. A `secret_value.read` attempt never reaches a state where there would be a value to redact — it is denied (`SECRET_VALUE_DISCLOSURE_FORBIDDEN`) before any Secret Manager interaction.

## Immutability

The Audit store exposes no update or delete operation for any event once written — this is a structural property of the storage role, not a policy rule that could be misconfigured away (Constitution Article III.2, case #18 in `docs/21_GOVERNANCE_CORE_SPEC.md`). A correction to a mistaken event is a new event referencing the original by `correlation_id`, never an edit in place.

## Replay after Governance unavailability

Locally queued `governance_unavailable`-path events (where queuing was itself possible) are appended to the chain in their original timestamp order once Governance returns, preserving `previous_event_hash` linkage as of the time they are actually appended — the chain records append order, not just occurrence order, and both are kept (`timestamp` for occurrence, chain position for append order) so a reviewer can see if there was a gap.

## Test cases specific to Audit Events

| Scenario | Setup | Expected outcome |
|---|---|---|
| Tamper detection | An event's stored fields are altered after write | Recomputed `event_hash` no longer matches; chain verification fails at that event |
| Missing conditional field | `policy_decision` event submitted without `reason_codes` | Schema validation rejects the event before it is appended |
| Audit unavailable at decision time | Audit sink unreachable when a `deny` decision is made | The deny still stands (fail-closed does not wait for audit to succeed to deny); but no `allow` may ever be granted without a corresponding successful audit write |
| Genesis event | First event in a new chain partition | `previous_event_hash` is 64 zero characters, not null or omitted |
| Out-of-order replay | Queued event from an outage appended later than events that occurred after it | `timestamp` reflects true occurrence order; chain position reflects append order; both retained |
