# IIOS Capability Model

**Version:** 0.2.0
**Status:** Specified, not implemented
**Parent:** `docs/21_GOVERNANCE_CORE_SPEC.md`
**Schema:** `governance/schemas/capability-token.schema.json`

## Purpose

A Capability is proof that the Governance API evaluated one specific action and authorized it. It is not an identity credential, not a session token, and not a substitute for the underlying system credential needed to actually perform the action (that credential stays in Secret Manager, per `AGENTS.md` Architecture rules).

## Payload vs. Envelope

The model separates two concerns that a flat token structure blurs together:

- **Capability Payload** — the *claims*: what is authorized, for whom, until when, under what policy. This is the data a signature is computed over.
- **Signed Capability Envelope** — the *transport artifact*: the payload plus the cryptographic proof that Governance actually issued it, unmodified. This is what is presented at consumption time.

Splitting them matters because it makes explicit a fact the flat version obscured: **a valid signature proves the payload came from Governance and is unmodified; it does not by itself prove the capability is currently usable.** Usability depends on server-side state (revocation, uses-remaining, current policy version) that is checked independently of, and in addition to, signature verification.

### Capability Payload

```text
capability_id      — unique identifier, referenced by every related audit event
issuer             — identifies the Governance API instance/environment that issued this
subject            — bound actor; not transferable to another actor
audience           — the executor/service this capability is valid for (prevents a token issued
                      for one execution surface being replayed against a different one)
action             — verb:resource_type, e.g. "merge:git_protected_branch"
resource            — concrete resource_ref; exact match required at consumption
environment         — local | staging | production | n/a
policy_version      — policy under which this was evaluated; checked against current active
                      version at consumption, not just at issuance
approval_id         — non-null for any Class C-derived capability
issued_at           — RFC 3339 UTC
not_before           — RFC 3339 UTC; capability is not valid before this instant
expires_at           — RFC 3339 UTC; short-lived, close to issued_at
max_uses            — intended use ceiling (see Server-side consumption state, below, for why
                      this is a ceiling declared in the payload, not the live counter)
constraints          — additional scope-narrowing conditions, e.g. max amount, allowed commit SHA
correlation_id       — propagated from the originating action-request
nonce                — unique per issuance, defends against payload-level replay independent of
                      max_uses tracking
```

### Signed Capability Envelope

```text
algorithm   — signature algorithm identifier
key_id      — which key signed this envelope
payload     — the Capability Payload, verbatim
signature   — signature over the canonical serialization of payload
```

This is what Governance returns to the caller and what the caller presents at consumption time. `governance/schemas/capability-token.schema.json` defines both shapes; the top-level schema is the envelope, with `payload` as a nested, independently referenceable definition.

## What is NOT in the payload, and why

`uses_remaining` and `revoked`/`revoked_at` are deliberately **absent** from both the Payload and the Envelope. A signed payload is immutable once issued — its signature would have to be recomputed on every consumption or every revocation if mutable consumption state lived inside it, which defeats the point of a signature as proof-of-issuance. Instead:

## Server-side consumption state

Consumption state — `uses_remaining` (starts at `max_uses`, decremented per successful consumption) and `revoked`/`revoked_at` — is tracked by Governance, keyed by `capability_id`, entirely separate from the signed envelope. This has direct consequences:

- **Consumption state is server-side.** The envelope's `max_uses` states intent at issuance; the live count is looked up, not read from the presented token.
- **`uses_remaining` is never a client-trusted assertion.** A client cannot claim "I still have uses left" — Governance's own record is authoritative, and a client presenting a stale or forged claim about remaining uses has no effect on the actual check.
- **Revocation and consumption state must both be checked before execution, every time**, regardless of signature validity. This means: a syntactically and cryptographically valid envelope for a revoked or exhausted capability must still be denied.
- **A valid signature does not imply a currently valid capability.** Signature verification answers "did Governance issue this, unmodified?" It does not answer "is it still good right now?" — that second question always requires a live server-side lookup, which is why consumption cannot happen offline (ties directly into the fail-closed rule: if Governance is unreachable, consumption state cannot be checked, so consumption is denied, not assumed valid because the signature checked out).

## No secrets in the token

Neither the Payload nor the Envelope ever contains a credential, API key, password, or raw secret value. This distinction matters concretely for the two verbs defined in `docs/21_GOVERNANCE_CORE_SPEC.md` — "Secret handling: value vs. reference": a capability can authorize `secret_reference.use` (case #10/#11 in the 20-case matrix) — the secret value flows directly from Secret Manager to the authorized execution context at consumption time, never through the capability itself. No capability can ever authorize `secret_value.read` (disclosure to a model/agent) — that verb has no allowed class, so no capability for it can be legitimately issued in the first place.

## Consumption checks (all required, in order; any failure is deny, none fail open)

1. Envelope signature valid for the claimed `algorithm`/`key_id`.
2. `now >= not_before` and `now < expires_at`.
3. Server-side record for `capability_id`: not revoked.
4. Server-side record for `capability_id`: `uses_remaining > 0`.
5. Server-side record for `capability_id`: this exact `nonce` has not already been consumed — **replay of an already-consumed capability (same `capability_id` + `nonce` presented again after a successful consumption) is denied with reason code `CAPABILITY_REPLAY_DENIED`**, distinct from `CAPABILITY_EXPIRED` (replay can be attempted well within the expiry window).
6. `policy_version` still active (else `POLICY_VERSION_MISMATCH`).
7. Presented `subject`, `audience`, `action`, `resource`, `environment` match the payload exactly.
8. Any `constraints` satisfied by the concrete execution parameters.

Only after all eight pass does `uses_remaining` decrement and the action proceed.

## Open questions for the Owner and security review

1. Signature format is deliberately **not chosen** in this specification. JWS, PASETO, and a bespoke `Ed25519`-over-JCS-canonicalized-payload scheme are all viable; the choice is deferred to implementation time, pending Owner decision and a dedicated security review. This document fixes the payload/envelope *shape*, not the cryptographic *format*.
2. Key custody (where signing keys live, rotation policy) — deferred with the signature format decision above.
3. Default `expires_at` ceiling per class (proposed starting point: Class A/B minutes-scale, Class C single-use tied to the consuming action's expected duration, not a fixed clock value).
4. Whether capability issuance itself should be rate-limited independent of the Cost Governance budget caps.
5. Whether `audience` should support multiple valid executors for one capability, or remain strictly single-valued for MVP.

## Test cases specific to Capabilities

| Scenario | Setup | Expected outcome |
|---|---|---|
| Expired capability | `now >= expires_at` at consumption | deny (`CAPABILITY_EXPIRED`) |
| Not yet valid | `now < not_before` at consumption | deny |
| Exhausted uses | Server-side `uses_remaining == 0` | deny |
| Replay of a consumed capability | Same `capability_id` + `nonce` presented again after a successful consumption | deny (`CAPABILITY_REPLAY_DENIED`), even though signature and expiry both still check out |
| Resource mismatch | Payload `resource` != presented resource (reclassification case) | deny; fresh action-request required |
| Revoked mid-flight | Capability revoked (server-side) after issuance, before consumption | deny (`CAPABILITY_REVOKED`), regardless of valid signature and unexpired window |
| Actor/audience mismatch | Payload `subject` or `audience` != presenting actor/executor | deny |
| Stale policy | `policy_version` on payload superseded before consumption | deny (`POLICY_VERSION_MISMATCH`) |
| Valid signature, revoked capability | Signature verifies correctly; server-side record says revoked | deny — this is the case that most directly demonstrates "valid signature does not imply currently valid" |
| Governance unreachable at consumption | Cannot check server-side revocation/uses/nonce state | deny (fail-closed; no offline capability validation for anything beyond cached Class A) |
