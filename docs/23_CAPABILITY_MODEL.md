# IIOS Capability Model

**Version:** 0.3.0
**Status:** Specified, not implemented
**Parent:** `docs/21_GOVERNANCE_CORE_SPEC.md`
**Schemas:** `governance/schemas/capability-claims.schema.json`, `governance/schemas/capability-protected-header.schema.json`, `governance/schemas/capability-token.schema.json`
**Cryptographic profile:** `docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md` — Capability envelope format (corrected 23 July 2026)

## Purpose

A Capability is proof that the Governance API evaluated one specific action and authorized it. It is not an identity credential, not a session token, and not a substitute for the underlying system credential needed to actually perform the action (that credential stays in Secret Manager, per `AGENTS.md` Architecture rules).

## Three contracts, not two

An earlier version of this document split "payload vs. envelope" but represented the envelope as a flat JSON object (`{algorithm, key_id, payload, signature}`). That shape is **not** a real JWS serialization: it left `alg`/`kid` outside the signed material and put a raw JSON payload next to a detached signature as the wire form. The Owner corrected this (`docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md`). The model now has three distinct contracts:

| Contract | Schema | What it is |
|---|---|---|
| **Claims** | `governance/schemas/capability-claims.schema.json` | The logical claims — what is authorized, for whom, until when. Never appears on the wire by itself. |
| **Protected header** | `governance/schemas/capability-protected-header.schema.json` | The decoded shape of the JWS Protected Header: `alg`, `kid`, `typ`. Signed, never external/unprotected. |
| **Wire token** | `governance/schemas/capability-token.schema.json` | The actual artifact presented at consumption: `{"format": "jws-compact", "token": "protected.payload.signature"}`. |

None of the three schemas contains a secret value, a credential, or mutable consumption state.

## Cryptographic profile

- **JWS Compact Serialization** (RFC 7515) — three Base64URL (unpadded) segments: `protected.payload.signature`. No JWS Unprotected Header; no JWS JSON Serialization.
- **`alg: "Ed25519"`** — the fully-specified JOSE algorithm identifier (RFC 9864), not the polymorphic `EdDSA` identifier. `EdDSA` is excluded from new issuance entirely; see ADR-0011.
- **`kid`** is a mandatory **protected-header** parameter, never an external field.
- **`typ: "iios-capability+jws"`** — mandatory protected-header parameter identifying the token type.
- **Single signer during MVP.**
- The claims are serialized via **RFC 8785 JCS** before Base64URL encoding and signing — see Issuance profile, below.
- No downgrade, no dynamic algorithm negotiation: the verifier's allowlist contains exactly one value, `Ed25519`.

## What is NOT in the claims, header, or wire token — and why

- **`uses_remaining`, `revoked`, `revoked_at`** are absent from the Claims (and everywhere else). A signed payload is immutable once issued — mutable consumption state living inside it would force re-signing on every consumption or revocation, which defeats the point of a signature as proof-of-issuance.
- **`algorithm`/`key_id` as external fields** are absent from the wire token. They live only inside the signed protected header (`alg`, `kid`) — an unprotected `algorithm`/`key_id` field would be attacker-controllable without invalidating the signature, which is exactly the class of confusion RFC 7515's protected-header design exists to prevent.
- **A separate `signature` field** is absent from the wire token — the signature is the token string's third dot-separated segment, not a sibling JSON property.
- **No secret value** appears in any of the three contracts.

## Server-side consumption state

Consumption state — `uses_remaining` (starts at `max_uses` from the Claims, decremented per successful consumption) and `revoked`/`revoked_at` — is tracked by Governance, keyed by `capability_id`, entirely separate from the signed structure. Consequences:

- **Consumption state is server-side.** The Claims' `max_uses` states intent at issuance; the live count is looked up, not read from the presented token.
- **`uses_remaining` is never a client-trusted assertion.**
- **Revocation and consumption state must both be checked before execution, every time**, regardless of signature validity.
- **A valid signature does not imply a currently valid capability.** Signature verification answers "did Governance issue this, unmodified?" It does not answer "is it still good right now?" — that always requires a live server-side lookup (fail-closed: if Governance is unreachable, consumption is denied, not assumed valid because the signature checked out).

## No secrets in any contract

Per `docs/21_GOVERNANCE_CORE_SPEC.md` — "Secret handling: value vs. reference": a capability can authorize `secret_reference.use` (case #10/#11) — the secret value flows directly from Secret Manager to the authorized execution context at consumption time, never through the capability. No capability can ever authorize `secret_value.read` — that verb has no allowed class, so no capability for it is legitimately issuable.

## I-JSON profile for JCS

Both the protected header and the capability claims must be valid **I-JSON** (RFC 7493) inputs before RFC 8785 JCS canonicalization is applied — JCS is only well-defined, interoperable, and reversible over I-JSON-compatible values. This is a **validation requirement checked before signing**, not a canonicalizer implementation (none is added by this change). Concretely, both objects must satisfy:

- **No duplicate property names** at any object level (JCS has no defined behavior for a duplicate key; the ambiguity must never reach the canonicalizer).
- **Unicode strings preserved exactly** — no further normalization (e.g. no NFC/NFD Unicode normalization, no case-folding, no trimming) is applied after validation and before canonicalization or after decoding. What was validated is exactly what gets canonicalized, and exactly what a verifier decodes back.
- **I-JSON-compatible numbers only.** Every number must be exactly representable as an IEEE 754 double, consistent with I-JSON's number profile.
- **No `NaN`, no `Infinity`/`-Infinity`, no non-JSON numeric literal or representation** (these are not legal JSON in the first place, but this is stated explicitly because some JSON encoders produce them non-conformantly).
- **Financial amounts, long numeric identifiers, and any value requiring precision a double cannot guarantee must be represented as strings**, never as a JSON number — this is the same rule already fixed for cost fields in `docs/25_AUDIT_EVENT_MODEL.md` and for financial amounts project-wide (`docs/21_GOVERNANCE_CORE_SPEC.md` — Quality requirements), applied here to any capability claim with the same characteristics (none of the current fixed claim fields are financial amounts, but `constraints` is open-ended and can carry them).
- **`constraints` is subject to all of the above**, recursively — it is the one open-ended object in the claims, and precisely because its shape isn't fixed by the schema, it is the most likely place an I-JSON violation would slip in.

**Any input that fails this profile is rejected before signing — it is never signed and never issued.** The issuer distinguishes which object failed:

- `CAPABILITY_CLAIMS_INVALID` — the claims object (duplicate keys, non-I-JSON numbers, `NaN`/`Infinity`, a value needing string representation left as a number, or a `capability-claims.schema.json` violation).
- `CAPABILITY_HEADER_INVALID` — the protected header object (duplicate keys, malformed JSON, a `capability-protected-header.schema.json` violation, or any I-JSON/JCS incompatibility in the header — the header's only three properties are all short strings, so this realistically catches malformed/duplicate-key headers rather than numeric issues).

No canonicalizer is implemented in this change; this section specifies the validation gate a future implementation's canonicalizer sits behind, not the canonicalizer itself.

## Issuance profile

1. Validate the protected header against `governance/schemas/capability-protected-header.schema.json` and the I-JSON profile above (else `CAPABILITY_HEADER_INVALID`).
2. Canonicalize the protected header via **RFC 8785 JCS**.
3. Base64URL-encode the canonical header bytes (UTF-8), **without padding**.
4. Validate the claims against `governance/schemas/capability-claims.schema.json` and the I-JSON profile above (else `CAPABILITY_CLAIMS_INVALID`).
5. Canonicalize the claims via **RFC 8785 JCS**.
6. Base64URL-encode the canonical claims bytes (UTF-8), **without padding**.
7. Form the JWS Signing Input: `BASE64URL(canonical_header) + "." + BASE64URL(canonical_claims)`.
8. Sign the Signing Input with the Ed25519 private key identified by `kid`.
9. Emit the wire token: `protected.payload.signature` (validates against `capability-token.schema.json`).

**RFC 7515 (JWS) does not require JCS or any particular canonicalization** — a JWS Signing Input is just "whatever bytes were Base64URL-encoded into the first two segments," and RFC 7515 leaves how those bytes were produced entirely to the application. **IIOS adopts JCS as its own internal deterministic profile** for producing the header and claims bytes at issuance time — not because JWS requires it, but so that two issuances of logically identical claims produce byte-identical payloads, which matters for reproducibility and for the audit trail (`docs/25_AUDIT_EVENT_MODEL.md`).

## Verification profile (mandatory order; any failure denies, none fail open)

1. Reject the token if it does not have exactly three dot-separated segments (`CAPABILITY_MALFORMED`).
2. Decode the protected header (first segment) **exactly as received — do not re-canonicalize or re-serialize it.**
3. Reject the header if it is malformed JSON, has duplicate or unrecognized properties, or fails `capability-protected-header.schema.json` (`additionalProperties: false`) (`CAPABILITY_HEADER_INVALID`).
4. Require: `alg == "Ed25519"` (else `CAPABILITY_ALGORITHM_DENIED`); `typ == "iios-capability+jws"` (else `CAPABILITY_TYPE_DENIED`); `kid` known and currently active (else `CAPABILITY_KEY_UNKNOWN`).
5. Verify the signature over the **original** JWS Signing Input **exactly as received** (`BASE64URL(protected) + "." + BASE64URL(payload)`, using the literal first and second segments of the presented token, byte for byte), using the Ed25519 public key identified by `kid` (else `CAPABILITY_SIGNATURE_INVALID`). **A received token is never re-serialized, re-canonicalized, or re-encoded before this check** — doing so would verify a signature against bytes the issuer never actually signed.
6. Only after the signature verifies: decode the claims (second segment) and validate against `capability-claims.schema.json` (else `CAPABILITY_CLAIMS_INVALID`). Signature verification and schema/policy validation are deliberately sequential and distinct — a cryptographically valid signature over structurally invalid claims is still rejected, and structurally valid claims with an invalid signature are rejected before their content is ever trusted.
7. Check: `issuer`; `subject`; `audience`; `not_before`; `expires_at`; `policy_version`; `environment`; `action`; `resource`.
8. Query server-side state: revocation; uses remaining; nonce/replay; kill switch (scope-matched, `docs/26_KILL_SWITCH_SPEC.md`).
9. Atomically consume one use before the action executes (decrement `uses_remaining`, record the `nonce` as consumed — atomic so two concurrent consumption attempts cannot both succeed against `max_uses: 1`).
10. Record the audit event.

## Reason codes

| Reason code | Verification step | Meaning |
|---|---|---|
| `CAPABILITY_MALFORMED` | 1 | Not exactly three segments, or a segment is not valid Base64URL/JSON |
| `CAPABILITY_HEADER_INVALID` | 3 (verification); Issuance profile step 1 | Header is malformed JSON, has duplicate property names, fails `capability-protected-header.schema.json`, or fails the I-JSON/JCS profile — checked at issuance (before signing) and again at verification (on the decoded header) |
| `CAPABILITY_ALGORITHM_DENIED` | 4 | `alg` is not exactly `Ed25519` (includes `EdDSA` and any other value) |
| `CAPABILITY_TYPE_DENIED` | 4 | `typ` is not exactly `iios-capability+jws` |
| `CAPABILITY_KEY_UNKNOWN` | 4 | `kid` does not match any known, currently active signing key |
| `CAPABILITY_SIGNATURE_INVALID` | 5 | Signature does not verify over the original Signing Input, presented exactly as received |
| `CAPABILITY_CLAIMS_INVALID` | 6 | Decoded claims fail `capability-claims.schema.json`, have duplicate property names, or fail the I-JSON/JCS profile (non-I-JSON number, `NaN`/`Infinity`, a value needing string representation left as a number) — checked at issuance (before signing) and again at verification (on the decoded claims) |
| `CAPABILITY_AUDIENCE_MISMATCH` | 7 | Presenting executor != claimed `audience` |
| `CAPABILITY_NOT_YET_VALID` | 7 | `now < not_before` |
| `CAPABILITY_EXPIRED` | 7 | `now >= expires_at` |
| `CAPABILITY_REVOKED` | 8 | Server-side record marks this `capability_id` revoked |
| `CAPABILITY_REPLAY_DENIED` | 8 | This `capability_id` + `nonce` already consumed |
| `CAPABILITY_POLICY_MISMATCH` | 7 | `policy_version` no longer active |
| `CAPABILITY_RESOURCE_MISMATCH` | 7 | Presented `resource`/`action`/`environment` != claims (reclassification case, `docs/21_GOVERNANCE_CORE_SPEC.md`) |

## Open questions for the Owner and security review

The cryptographic **format** is now fully resolved (JWS Compact, `alg: Ed25519`, `kid` in protected header, `typ: iios-capability+jws`; ADR-0011, corrected 23 July 2026). Remaining, genuinely open:

1. ~~Signature format~~ — **Resolved**: JWS Compact Serialization, `alg: Ed25519`, mandatory `kid`/`typ` in the protected header. PASETO, a bespoke scheme, and the polymorphic `EdDSA` identifier were all considered and excluded (ADR-0011 — Capability envelope format, Alternatives considered and discarded).
2. ~~Key custody~~ — **Resolved**: private key in KMS/HSM/external Vault, non-exportable where supported, public key via trusted registry/JWKS, 90-day rotation, 24h maximum overlap for a previous key (ADR-0011 — Key custody).
3. ~~Default `expires_at` ceiling per class~~ — **Resolved**: Class A max 10 min (when a capability is required), Class B max 5 min, Class C max 2 min, Class D never issued; B and C default `max_uses: 1` (ADR-0011 — Capability TTLs by class).
4. ~~Whether capability issuance should be rate-limited independent of Cost Governance budgets~~ — **Resolved**: yes, independent; initial values A=60/min, B=10/min, C=5/hour, D=0, per `subject` (ADR-0011 — Rate limiting).
5. ~~Whether `audience` should support multiple executors~~ — **Resolved**: single-valued for MVP; multiple executors deferred (ADR-0011 — `audience`).
6. **Still open**: which specific KMS/HSM/Vault product, and its exact IAM/access-control configuration — ADR-0011 fixes the custody *category*, not the concrete provider.
7. **Still open**: the JWKS/trusted-registry endpoint's own hosting, availability, and caching policy for public-key distribution.

No cryptography is implemented by this document; issuance and verification above are a specification for a future implementation, not code.

## Examples

All values below are **fictitious and non-sensitive** — placeholder UUIDs, no real repository state, no real key material. They illustrate shape only.

### Protected header (decoded)

Validates against `governance/schemas/capability-protected-header.schema.json`:

```json
{
  "alg": "Ed25519",
  "kid": "iios-gov-2026-07-key-01",
  "typ": "iios-capability+jws"
}
```

### Claims (decoded)

Includes every field `governance/schemas/capability-claims.schema.json` requires, plus the two optional fields (`approval_id`, `constraints`):

```json
{
  "capability_id": "b1f0c1a0-6e2f-4b3a-9a1a-000000000001",
  "issuer": "iios-governance-api:staging",
  "subject": "actor:orchestrator-01",
  "audience": "executor:git-service",
  "action": "merge:git_protected_branch",
  "resource": "repo:IIOS-Complete-v1.2.0:branch:feature/example",
  "environment": "staging",
  "policy_version": "1.0.0",
  "approval_id": "b1f0c1a0-6e2f-4b3a-9a1a-000000000002",
  "issued_at": "2026-07-23T12:00:00Z",
  "not_before": "2026-07-23T12:00:00Z",
  "expires_at": "2026-07-23T12:02:00Z",
  "max_uses": 1,
  "constraints": {
    "allowed_commit_sha": "deadbeefcafefeed0011223344556677"
  },
  "correlation_id": "b1f0c1a0-6e2f-4b3a-9a1a-000000000003",
  "nonce": "b1f0c1a0-6e2f-4b3a-9a1a-000000000004"
}
```

Note `allowed_commit_sha` and every timestamp/identifier above are strings, per the I-JSON profile — nothing here is a claim that needed numeric representation, but this is the pattern any future financial-amount or long-numeric-ID constraint must follow.

### Wire token (illustrative — NOT a real signature)

The protected header and claims above, Base64URL-encoded (unpadded) exactly as shown — **the third segment is 64 arbitrary bytes, not an Ed25519 signature produced by any key.** No cryptographic signing occurred to produce this example; it exists only to show the three-segment shape and character set.

```text
eyJhbGciOiJFZDI1NTE5Iiwia2lkIjoiaWlvcy1nb3YtMjAyNi0wNy1rZXktMDEiLCJ0eXAiOiJpaW9zLWNhcGFiaWxpdHkrandzIn0.eyJhY3Rpb24iOiJtZXJnZTpnaXRfcHJvdGVjdGVkX2JyYW5jaCIsImFwcHJvdmFsX2lkIjoiYjFmMGMxYTAtNmUyZi00YjNhLTlhMWEtMDAwMDAwMDAwMDAyIiwiYXVkaWVuY2UiOiJleGVjdXRvcjpnaXQtc2VydmljZSIsImNhcGFiaWxpdHlfaWQiOiJiMWYwYzFhMC02ZTJmLTRiM2EtOWExYS0wMDAwMDAwMDAwMDEiLCJjb25zdHJhaW50cyI6eyJhbGxvd2VkX2NvbW1pdF9zaGEiOiJkZWFkYmVlZmNhZmVmZWVkMDAxMTIyMzM0NDU1NjY3NyJ9LCJjb3JyZWxhdGlvbl9pZCI6ImIxZjBjMWEwLTZlMmYtNGIzYS05YTFhLTAwMDAwMDAwMDAwMyIsImVudmlyb25tZW50Ijoic3RhZ2luZyIsImV4cGlyZXNfYXQiOiIyMDI2LTA3LTIzVDEyOjAyOjAwWiIsImlzc3VlZF9hdCI6IjIwMjYtMDctMjNUMTI6MDA6MDBaIiwiaXNzdWVyIjoiaWlvcy1nb3Zlcm5hbmNlLWFwaTpzdGFnaW5nIiwibWF4X3VzZXMiOjEsIm5vbmNlIjoiYjFmMGMxYTAtNmUyZi00YjNhLTlhMWEtMDAwMDAwMDAwMDA0Iiwibm90X2JlZm9yZSI6IjIwMjYtMDctMjNUMTI6MDA6MDBaIiwicG9saWN5X3ZlcnNpb24iOiIxLjAuMCIsInJlc291cmNlIjoicmVwbzpJSU9TLUNvbXBsZXRlLXYxLjIuMDpicmFuY2g6ZmVhdHVyZS9leGFtcGxlIiwic3ViamVjdCI6ImFjdG9yOm9yY2hlc3RyYXRvci0wMSJ9.AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-Pw
```

As a `capability-token.schema.json` instance:

```json
{
  "format": "jws-compact",
  "token": "<the three-segment string above>"
}
```

Verified structurally: exactly three segments, every character in `[A-Za-z0-9_-]`, no `=` padding, no spaces, no `•`, no `...` abbreviation — the string above is presented in full, not truncated. **No signature verification was performed or claimed** — the third segment is arbitrary bytes, not a valid Ed25519 signature over the first two segments, and must never be treated as one.

## Test cases specific to Capabilities

| Scenario | Setup | Expected outcome |
|---|---|---|
| Malformed token | Fewer or more than three dot-separated segments | deny (`CAPABILITY_MALFORMED`) |
| Algorithm downgrade attempt | `alg: "EdDSA"` or `alg: "none"` presented | deny (`CAPABILITY_ALGORITHM_DENIED`) — never accepted as a legacy fallback |
| Wrong `typ` | `typ` missing or not `iios-capability+jws` | deny (`CAPABILITY_TYPE_DENIED`) |
| Unknown key | `kid` not in the active key set | deny (`CAPABILITY_KEY_UNKNOWN`) |
| Tampered payload | Any byte of `protected` or `payload` altered post-signing | deny (`CAPABILITY_SIGNATURE_INVALID`) |
| Expired capability | `now >= expires_at` at consumption | deny (`CAPABILITY_EXPIRED`) |
| Not yet valid | `now < not_before` at consumption | deny (`CAPABILITY_NOT_YET_VALID`) |
| Exhausted uses | Server-side `uses_remaining == 0` | deny |
| Replay of a consumed capability | Same `capability_id` + `nonce` presented again after a successful consumption | deny (`CAPABILITY_REPLAY_DENIED`), even though signature and expiry both still check out |
| Resource mismatch | Claims' `resource`/`action` != presented (reclassification case) | deny (`CAPABILITY_RESOURCE_MISMATCH`); fresh action-request required |
| Revoked mid-flight | Capability revoked (server-side) after issuance, before consumption | deny (`CAPABILITY_REVOKED`), regardless of valid signature and unexpired window |
| Audience mismatch | Claims' `audience` != presenting executor | deny (`CAPABILITY_AUDIENCE_MISMATCH`) |
| Stale policy | `policy_version` on claims superseded before consumption | deny (`CAPABILITY_POLICY_MISMATCH`) |
| Valid signature, revoked capability | Signature verifies correctly; server-side record says revoked | deny — the case that most directly demonstrates "valid signature does not imply currently valid" |
| Governance unreachable at consumption | Cannot check server-side revocation/uses/nonce state | deny (fail-closed; no offline capability validation for anything beyond cached Class A) |
| Duplicate/unknown header property | Protected header has an extra property beyond `alg`/`kid`/`typ`, or a duplicated key | deny (`CAPABILITY_HEADER_INVALID`) — `additionalProperties: false` plus the no-duplicate-keys I-JSON rule |
| Non-I-JSON number in claims | A claim (e.g. inside `constraints`) carries `NaN`, `Infinity`, or a number not exactly representable as an IEEE 754 double | rejected before signing (`CAPABILITY_CLAIMS_INVALID`) — never issued |
| Financial amount as a raw number | A `constraints` value representing money is a JSON number instead of a decimal string | rejected before signing (`CAPABILITY_CLAIMS_INVALID`) |
| Duplicate key in claims | Claims JSON has the same property name twice at the same level | rejected before signing (`CAPABILITY_CLAIMS_INVALID`); also re-checked at verification on the decoded claims |
