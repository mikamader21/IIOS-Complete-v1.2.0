"""Policy Engine — evaluates one ActionItem against the loaded Invariant
Kernel first (non-overridable), then the loaded policy bundle.

docs/22_POLICY_ENGINE_EVALUATION.md:
  - Kernel match is deny and evaluation stops — no rule can override it.
  - Deny-by-default: no matching rule => deny.
  - Precedence: exact match beats wildcard; higher `precedence` wins
    among equally specific matches; deny wins over allow, require_approval
    wins over allow, on any remaining tie (Constitution Article X, safer
    interpretation).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iios_governance.domain.action_classifier import ClassificationResult
from iios_governance.domain.models import ActionItem, DecisionOutcome
from iios_governance.domain.reason_codes import POLICY_NO_MATCHING_RULE, UNCLASSIFIED_RESOURCE

# classifier reason code -> Invariant Kernel id this categorical deny maps to.
_REASON_TO_INVARIANT_ID = {
    "CLASS_D_PROHIBITED": "INV-002",
    "PROTECTED_AUTHORITY_PATH": "INV-003",
    "SECRET_VALUE_DISCLOSURE_FORBIDDEN": "INV-004",
}

_EFFECT_STRICTNESS = {"allow": 0, "require_approval": 1, "deny": 2}


@dataclass(frozen=True)
class ItemEvaluation:
    outcome: DecisionOutcome
    reason_codes: tuple[str, ...]
    matched_invariants: tuple[str, ...] = ()
    matched_rules: tuple[str, ...] = ()
    offline_read_allowed: bool = False


def _kernel_matched_invariants(
    reason_codes: tuple[str, ...], kernel_invariants: list[dict[str, Any]]
) -> tuple[str, ...]:
    known_ids = {inv["id"] for inv in kernel_invariants}
    matched = []
    for code in reason_codes:
        inv_id = _REASON_TO_INVARIANT_ID.get(code)
        if inv_id and inv_id in known_ids:
            matched.append(inv_id)
    return tuple(matched)


def evaluate_item(
    item: ActionItem,
    classification: ClassificationResult,
    kernel_invariants: list[dict[str, Any]],
    policy_bundle: dict[str, Any],
) -> ItemEvaluation:
    # 1. Kernel short-circuit. classify_item() already flagged categorical
    #    denies with a Kernel-mappable reason code; nothing in the policy
    #    bundle is even consulted in that case.
    if classification.reason_codes and any(
        code in _REASON_TO_INVARIANT_ID for code in classification.reason_codes
    ):
        matched = _kernel_matched_invariants(classification.reason_codes, kernel_invariants)
        return ItemEvaluation(
            outcome=DecisionOutcome.DENY,
            reason_codes=classification.reason_codes,
            matched_invariants=matched,
        )

    if classification.reason_codes == (UNCLASSIFIED_RESOURCE,):
        # No table entry, no policy rule can exist for it either — deny by
        # default, not a guess at A.
        return ItemEvaluation(outcome=DecisionOutcome.DENY, reason_codes=(UNCLASSIFIED_RESOURCE,))

    # 2. Policy bundle rule matching.
    candidates = []
    for rule in policy_bundle["rules"]:
        m = rule["match"]
        if (
            _field_matches(m["verb"], item.verb)
            and _field_matches(m["resource_type"], item.resource_type)
            and _field_matches(m["environment"], item.environment)
        ):
            specificity = sum(
                1 for f in (m["verb"], m["resource_type"], m["environment"]) if f != "*"
            )
            candidates.append((specificity, rule))

    if not candidates:
        return ItemEvaluation(outcome=DecisionOutcome.DENY, reason_codes=(POLICY_NO_MATCHING_RULE,))

    max_specificity = max(c[0] for c in candidates)
    most_specific = [rule for spec, rule in candidates if spec == max_specificity]
    max_precedence = max(r["precedence"] for r in most_specific)
    top = [r for r in most_specific if r["precedence"] == max_precedence]

    # Tie-break: strictest effect wins (deny > require_approval > allow).
    winner = max(top, key=lambda r: _EFFECT_STRICTNESS[r["effect"]])

    reason_codes = []
    if winner.get("reason_code"):
        reason_codes.append(winner["reason_code"])
    elif winner["effect"] == "require_approval":
        reason_codes.append("APPROVAL_REQUIRED")

    return ItemEvaluation(
        outcome=DecisionOutcome(winner["effect"]),
        reason_codes=tuple(reason_codes),
        matched_rules=(winner["id"],),
        offline_read_allowed=bool(winner.get("offline_read_allowed", False)),
    )


def _field_matches(pattern: str, value: str) -> bool:
    return pattern == "*" or pattern == value
