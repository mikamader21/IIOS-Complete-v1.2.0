# IIOS Approval Model

**Version:** 0.1.0
**Status:** Specified, not implemented
**Parent:** `docs/21_GOVERNANCE_CORE_SPEC.md`
**Schema:** `governance/schemas/approval.schema.json`

## Purpose

Gate every Class C action on an authenticated human decision, distinct from the requester, before a capability can be issued. The Approval Service does not decide whether an action is Class C — that is the Policy Engine's job — it only manages the lifecycle of the human decision once required.

## States

Exactly the seven states specified:

```text
not_required → (no approval flow entered; Class A/B items skip this entirely)
pending       → approval requested, awaiting decision(s)
approved      → sufficient approvals recorded, capability may be issued
rejected      → an approver rejected; capability never issued for this request
expired       → expires_at passed with state still pending
revoked       → an approved (possibly consumed) approval was withdrawn
consumed      → a capability issued from this approval has been used
```

Valid transitions: `pending → approved | rejected | expired`; `approved → consumed | revoked`; `consumed → revoked` (revocation after consumption stops future reuse/renewal, it does not undo the already-executed action — that is Audit's evidence record, not a time machine). No other transition is valid; in particular `rejected` and `expired` are terminal.

## Who can approve

Default MVP: **Owner only**. `approver_roles` (`approval.schema.json`) also allows `delegated_approval_authority` for a future explicit, scoped, revocable, logged delegation per Constitution Article I.2 — not active by default in Foundation, and never inferred from framework availability (mirrors the Cowork boundary principle in ADR-0008: "Connector availability never constitutes authorization").

## Approver authentication

The approver authenticates on a channel independent from whatever produced the request — never inferred from the same conversational context, silence, or prior behavior (Constitution Article I.3). `decisions[].auth_method` records `owner_session` or `delegated_token`; a request-side `auth_method` value is never accepted as an approval decision.

## Expiration

Every approval carries `expires_at`, set at creation. Proposed default TTL (Open question for the Owner, `docs/21_GOVERNANCE_CORE_SPEC.md` item 3): 24 hours for a typical Class C action, shorter for higher-risk resource types (e.g. production deployment, secret rotation) at the policy author's discretion via `docs/22_POLICY_ENGINE_EVALUATION.md` rule conditions. An approval that hits `expires_at` while still `pending` transitions to `expired` and cannot be approved after the fact — a fresh action-request is required.

## Rejection

Rejection is explicit and requires a `reason_code`. A rejected request's exact `(idempotency_key request hash)` cannot be silently resubmitted to try for a different answer — the requester must submit a materially different request (Constitution's prohibition on inferring authorization from repeated attempts).

## Revocation

The approver role (Owner or delegated Approval Authority) may revoke an `approved` or `consumed` approval at any time. Revocation immediately prevents any further capability issuance or renewal tied to that `approval_id`; it emits `approval_revoked` and, if a live capability exists, triggers `capability_revoked` for it.

## Multi-person approval

Supported structurally via `required_approvals` and `decisions[]` but defaults to `required_approvals: 1` (Owner) for MVP. Not activated for any case in the 20-case matrix; reserved for a future ratified policy that names a specific higher-risk action requiring it (Open question 4, `docs/21_GOVERNANCE_CORE_SPEC.md`).

## Self-approval prevention

The rule is `decisions[].approver_id` MUST NOT equal `requested_by`. This is a cross-field inequality between two independent properties, which JSON Schema Draft 2020-12 cannot express or enforce on its own — Draft 2020-12 has no keyword that compares the value of one property against another sibling or ancestor property. `approval.schema.json` documents the rule via `$comment` for readability; it is not, and must not be presented as, the enforcement mechanism. Enforcement is layered:

1. **Policy Engine** applies the `approver_id != requested_by` inequality as an explicit evaluation-time check before returning `approved` for any decision (`docs/22_POLICY_ENGINE_EVALUATION.md`). A violation is `deny` with reason code `SELF_APPROVAL_FORBIDDEN`.
2. **Tests** — the mandatory test suite (`docs/21_GOVERNANCE_CORE_SPEC.md`, `docs/22_POLICY_ENGINE_EVALUATION.md`) includes a self-approval-attempt case that must resolve to `deny` before any `policy_version` is promoted.
3. **Approval Service** re-checks the inequality independently at the moment an approval is about to be consumed (i.e. before a capability derived from it is issued), not only at decision time — a defense-in-depth re-check, not a duplicate of step 1's trust boundary.

The Orchestrator actor type can never itself hold an approver role, because `action-request.schema.json#/$defs/actor/actor_type` is a closed enum that does not include an approval-capable role for `orchestrator` — that part genuinely is a structural, schema-level guarantee (enum membership is something JSON Schema can enforce), unlike the `approver_id != requested_by` cross-field comparison above.

## Evidence

`evidence_ref` points to the action-request and policy-decision the approver actually saw, so the decision is reproducible: given the evidence bundle, a later reviewer can confirm the approver was shown the true scope of what they approved, not a summarized or narrowed version.

## Relation to the Owner

Approval Authority is the Owner by default (Master Charter authority hierarchy). It is a distinct node from Governance/Policy and from the Orchestrator — capability never implies authority, and the Approval Authority is not something the Orchestrator, a model, or a runtime can hold or borrow.

## Test cases specific to Approvals

| Scenario | Setup | Expected outcome |
|---|---|---|
| Self-approval attempt | `approver_id == requested_by` | Policy Engine denies at decision time (`SELF_APPROVAL_FORBIDDEN`); Approval Service re-checks and denies again if presented at consumption time |
| Expired approval | `now > expires_at`, state still `pending` | Auto-transitions to `expired`; any later approval attempt is rejected |
| Approval then resource change | Approved for resource X, execution attempts resource Y | Capability never issued for Y; fresh request required (ties to Action Classifier reclassification) |
| Revoked after consumption | Approval `consumed`, later `revoked` | No new capability derivable from this approval; already-executed action stands, recorded as-is in Audit |
| Multi-approval partial | `required_approvals: 2`, one `approved` decision recorded | State remains `pending`, not `approved`, until the second decision arrives |
| Rejection resubmission | Same request resubmitted unchanged after rejection | Rejected again; unchanged `idempotency_key`/request hash does not get a second independent evaluation |
