# ADR-0012 — Policy Bundle Concrete Format

Status: Proposed
Date: 23 July 2026
Owner: IIOS Owner (ratification pending)

## Context

`docs/22_POLICY_ENGINE_EVALUATION.md` and ADR-0011 fix the *conditions* a Policy Engine format must satisfy (closed declarative language, no code, allowlisted operators, deterministic precedence, deny-by-default, checksum-protected, depth/size limits) but left the concrete JSON structure unspecified. `GOV-IMP-001` (Governance Core implementation skeleton) needs an actual, loadable bundle to evaluate against, so this ADR proposes the concrete schema (`governance/schemas/policy-bundle.schema.json`) and the MVP bundle instance (`governance/policy-bundles/mvp/`) built to it.

## Decision

- A policy bundle is a JSON document validating against `governance/schemas/policy-bundle.schema.json`: `schema_version`, `policy_version`, `default_decision` (fixed `"deny"`), `limits` (`max_rules`, `max_condition_depth`), and `rules[]`.
- Each rule: `id` (pattern `POL-*`), `match` (`verb`/`resource_type`/`environment`, each an exact string or `*`), optional `conditions[]` (allowlisted `op` only: `equals`, `not_equals`, `in`, `not_in`, `greater_than`, `less_than`, `matches_prefix`), `action_class`, `effect` (`allow`/`deny`/`require_approval`), `precedence` (integer), optional `offline_read_allowed` (Class A only), optional explicit `reason_code`.
- The bundle is protected by a `manifest.json` checksum file, byte-for-byte mirroring the Invariant Kernel's existing pattern (`governance/invariant-kernel/manifest.json`), including the same canonical (CRLF/CR-to-LF) hashing already shipped in `scripts/verify_invariant_kernel.py` — one canonicalization method reused, not a second one invented, for this specific file-portability problem (distinct from the audit-event JCS problem, per the correction already recorded in `docs/25_AUDIT_EVENT_MODEL.md`).
- Kernel invariants are evaluated separately, before any policy rule, by the domain classifier/Kernel-check step — a policy bundle rule can never override an `INV-*` deny. This bundle only encodes what is *not* already fully decided by the Kernel.

## Alternatives considered

- **Embed Kernel-equivalent deny rules inside the policy bundle itself** (e.g. a rule for "never allow trade execution"). Discarded: the Invariant Kernel already owns that decision (INV-002); duplicating it in the policy bundle creates two places that could drift out of sync. The bundle only contains rules for actions the Kernel does not already unconditionally deny.
- **Free-form condition expressions** (e.g. a small expression language). Discarded per ADR-0011/docs/22's explicit "no code, no scripts, no arbitrary expressions" condition — the allowlisted-operator array is more verbose but auditable by inspection alone.

## Consequences

Implementers get a concrete, loadable format instead of a set of conditions to satisfy from scratch. The cost: this ADR is **Proposed**, not **Ratified** — the skeleton's tests and code work against it, but the Owner has not yet formally ratified this specific schema the way ADR-0010/ADR-0011 were ratified. A future ratification (or amendment) may change field names or the condition operator set; `policy_version` and the bundle's own checksum make such a change auditable and non-silent.

## Security/financial impact

None directly. No policy bundle in this skeleton grants any Class D action, and the MVP bundle's Class C rules all resolve to `require_approval`, never `allow`.

## Evidence

- `governance/schemas/policy-bundle.schema.json`
- `governance/policy-bundles/mvp/policy.json`, `governance/policy-bundles/mvp/manifest.json`
- `tests/governance/test_policy_engine.py`

## Rollback/review date

Rollback: revert this branch before merge; no ratified document is touched.
Review date: before this ADR could be considered for ratification, and at any future Policy Engine format change.
