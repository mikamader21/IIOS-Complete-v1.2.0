# IIOS Policy Engine — Evaluation and Specification

**Version:** 0.1.0
**Status:** Specified, not implemented
**Parent:** `docs/21_GOVERNANCE_CORE_SPEC.md`

## Responsibilities

Evaluate one action-request's items against the Invariant Kernel and the active policy bundle, and return a `policy-decision` (`governance/schemas/policy-decision.schema.json`). The Policy Engine does not authenticate actors, does not manage approvals, and does not issue capabilities — it only decides `allow` / `deny` / `require_approval` per item, deterministically.

## Policy format

A policy bundle is a JSON document (schema not defined in this change; deferred to implementation, structurally analogous to `governance/invariant-kernel/schema.json`) containing an ordered list of rules:

```text
rule:
  id                  — stable identifier, e.g. "POL-GIT-001"
  match:
    verb              — exact string or "*"
    resource_type     — exact string or "*"
    environment       — exact string or "*"
  conditions          — optional attribute expressions (e.g. budget_context.domain == "trading")
  action_class        — A | B | C | D
  effect              — allow | deny | require_approval
  precedence          — integer, higher wins among matching rules of equal specificity
  policy_version      — semantic version this rule belongs to
```

A rule set is versioned as a whole (`policy_version`), never edited in place — a change is a new version, evaluated only after it passes the mandatory tests below.

## Precedence

Evaluation order, most authoritative first:

1. **Invariant Kernel** (`governance/invariant-kernel/invariants.json`) — non-overridable. A Kernel match is `deny` and evaluation stops; no policy rule can produce `allow` over a Kernel deny.
2. **Explicit Owner directive** tied to a ratified ADR or approval — narrowly scoped, logged, revocable (Constitution Art. I.2).
3. **Domain policy rules**, most-specific match wins: exact `(verb, resource_type, environment)` beats a wildcard in any field; among equally specific rules, higher `precedence` wins; among ties, `deny` wins over `allow` and `require_approval` wins over `allow` (the safer interpretation, Constitution Article X).
4. **Default**: deny.

## Deny-by-default

No matching rule at any level means deny. This is enforced structurally: the evaluator's final fallthrough branch is `deny`, not `allow`; there is no "default allow" code path to disable.

## Evaluation against the Invariant Kernel

Every evaluation first runs the eight `INV-*` invariants (`governance/invariant-kernel/invariants.json`) against the request. This is a fixed, non-configurable first pass — it does not consume a `precedence` slot because it is not a policy rule, it is the floor policy rules sit on.

## Policy version

Every `policy-decision`, `capability-token`, and relevant `audit-event` embeds the exact `policy_version` evaluated. This makes every decision reproducible without needing the live policy store: given the evidence bundle and the referenced `policy_version`, a reviewer can re-derive the same outcome from the archived policy bundle for that version.

## Cached policies

Only Class A decisions may be served from a cache, and only when the cached entry:

- carries a `policy_version` still marked active (not superseded or revoked);
- has not exceeded its cache TTL;
- explicitly authorizes offline read-only operation for the matched rule.

Class B, C, and D decisions are never cached for offline use — per the fail-closed rule, their absence of a live Policy Engine is a `deny`, not a cache lookup.

## Expiration

Cache TTL is a policy-bundle-level parameter, not hardcoded. Proposed MVP ceiling: 15 minutes for Class A cache entries (Open question for the Owner in `docs/21_GOVERNANCE_CORE_SPEC.md`). A policy bundle itself does not "expire" — it remains valid until explicitly superseded by a new `policy_version`.

## Behavior on unavailability

Identical to the Governance API fail-closed rule (`docs/21_GOVERNANCE_CORE_SPEC.md` — Fail-closed); not restated with different semantics here to avoid drift between documents.

## Explanation of decisions

Every `policy-decision` carries machine-readable `reason_codes` (required) and an optional human-readable `explanation` string for Control Center display (`docs/11_CONTROL_CENTER_PRD.md` Approvals/Audit modules). `explanation` is advisory only; `reason_codes` and `matched_rules`/`matched_invariants` are the authoritative record.

## Mandatory tests before promoting a `policy_version`

A new policy bundle version may not become active until it passes:

1. every row of the 20-case matrix in `docs/21_GOVERNANCE_CORE_SPEC.md` still resolves to the documented class/decision;
2. the conceptual test matrix in `docs/21_GOVERNANCE_CORE_SPEC.md` (allow, deny, require_approval, expired approval, expired capability, duplicate request, replay, policy mismatch, budget exceeded, Governance unavailable, audit unavailable, kill switch active, Kernel semantic modification);
3. no rule in the new bundle can produce `allow` for anything the Invariant Kernel denies (static check: intersect rule match patterns against each `INV-*` enforcement scope);
4. `governance/schemas/*.json` instance validation for every schema this document's outputs reference.

This document does not implement a test runner; it fixes what "passing" means so the future test runner has an unambiguous target.

## Technology comparison

| Option | Fit for IIOS Foundation/MVP | Cost |
|---|---|---|
| **Custom JSON rules** (this bundle's format, extending the existing Invariant Kernel schema/checksum pattern) | Matches the pattern already ratified for the Kernel; trivially schema-validated and unit-tested with the same tooling as `scripts/verify_invariant_kernel.py`; zero new runtime dependency or attack surface | Reinvents evaluation semantics; no formal-verification tooling; precedence/conflict resolution must be hand-built and proven correct by the mandatory test suite above |
| **Open Policy Agent / Rego** | Purpose-built policy language, mature ecosystem, built-in decision logs and partial evaluation for explanation | New external dependency and runtime (OPA server or embedded Go/Wasm lib) not yet in `docs/10_INFRASTRUCTURE.md`'s approved service list; Rego has a real learning curve; adds an upgrade/patch surface before Foundation's infrastructure scope allows it |
| **Cedar** | Formal authorization semantics, policy analysis/validation tooling, designed for exactly this problem class | Younger ecosystem outside AWS tooling; still a new dependency; less prior art to audit against for a one-person-Owner system at this stage |
| **Casbin** | Lightweight, multi-language SDKs, common RBAC/ABAC support | Model-file (`.conf`) approach is weaker for the fine-grained conditions IIOS needs (budget context, environment, risk signals); weaker native support for deny-by-default + explanation together; still a new dependency |

## Mandatory conditions on the custom JSON rules format

Choosing "custom JSON rules" for MVP is not a license to build an ad hoc scripting system that happens to be JSON-shaped. The following conditions are binding on the format regardless of who implements it or when, precisely because a policy engine that can run arbitrary logic is a policy engine that can no longer be reasoned about or audited the way this specification assumes:

- **Closed, declarative language.** A rule is data — match conditions, a class, an effect, a precedence number. It is never a program.
- **No code, scripts, or arbitrary expressions.** No `eval`, no embedded language runtime, no string-interpolated conditions parsed as code. If a condition needs logic beyond attribute comparison, that is a signal the rule needs to be split or the schema needs a new explicit field, not a signal to add an expression language.
- **Operators via an explicit allowlist.** Conditions may use only a fixed, published set of comparison operators (e.g. `equals`, `in`, `not_in`, `greater_than`, `less_than`, `matches_prefix`) — never an open-ended operator namespace a rule author could extend informally.
- **Deterministic evaluation.** The same `(action-request, policy_version, kernel_checksum)` always produces the same decision. No clock-dependent, random, or environment-dependent branching inside a rule (time-boxing, e.g. approval TTLs, is a property of the Approval/Capability model, not a rule-internal condition).
- **Explicit order and precedence.** Already fixed above (Precedence section); restated here because it is a condition on the format, not just a description of current behavior — precedence must remain a declared integer field, never "whichever rule the engine happens to load last."
- **Conflict resolves to deny or the more restrictive class**, never to allow — the same safer-interpretation principle as Constitution Article X, applied at the rule-conflict level specifically.
- **Schema-versioned.** Every policy bundle validates against a published schema for the bundle format itself (analogous to `governance/invariant-kernel/schema.json`), and that schema is itself versioned.
- **Depth and size limits.** A policy bundle has a maximum rule count and a maximum condition-nesting depth, both enforced at load time — an unbounded bundle is itself a denial-of-service and auditability risk, independent of what any individual rule says.
- **Signed or checksummed policy bundles.** Every active bundle has a manifest-recorded checksum, following the exact pattern already ratified for `governance/invariant-kernel/manifest.json` — a policy bundle whose bytes don't match its recorded checksum must fail closed exactly as an Invariant Kernel mismatch does.
- **Equivalence tests required before promotion.** Beyond the mandatory test suite (above), a new `policy_version` must be shown to produce the *same* decisions as the prior version for every case not intentionally changed, so an editor can see exactly what a policy change altered.
- **Future migration to Cedar or OPA remains possible**, and the format is deliberately kept restricted (no engine-specific cleverness) precisely so that migration stays a re-encoding exercise, not a re-design.

## Recommendation for MVP

**Custom JSON rules**, not installed by this change, and not an irreversible implementation decision — it is a recommendation subject to the mandatory conditions above, reversible via a future ADR if measured complexity outgrows them. Rationale: it is the only option that adds zero new infrastructure to the currently-approved scope (`AGENTS.md` — "Current allowed scope" lists "policy-engine skeleton," not a third-party policy runtime), it reuses the checksum/manifest/verifier pattern already ratified for the Invariant Kernel, and it keeps the mandatory-test bar (above) trivially checkable with the same Python-script approach already in `scripts/`. Charter's "Add queues, GPU or Kubernetes only from measured demand" principle applies equally here: adopt OPA, Cedar, or Casbin only once real rule-set complexity or multi-service reuse creates measured demand, via a future ADR.

Migration path is kept open: policy rules are written to remain expressible in Rego/Cedar's data model (flat match conditions, explicit precedence, no engine-specific cleverness), so a future migration would be a re-encoding, not a re-design.

## Additional test cases specific to the Policy Engine

| Scenario | Setup | Expected outcome |
|---|---|---|
| Kernel/policy conflict | A policy rule would `allow` an action an `INV-*` invariant denies | `deny`; Kernel wins, flagged as a policy-bundle authoring error, not silently resolved |
| Ambiguous precedence | Two rules of equal specificity and equal `precedence` disagree | `deny` (or `require_approval` if either rule says so) — safer interpretation wins, never `allow` |
| Stale `policy_version` reference | A capability references a `policy_version` no longer active | `deny` (`POLICY_VERSION_MISMATCH`) |
| Empty rule set | Policy bundle loads with zero rules (e.g. corrupt deploy) | `deny` for everything except what the Kernel itself explicitly and unconditionally allows (none currently) |
