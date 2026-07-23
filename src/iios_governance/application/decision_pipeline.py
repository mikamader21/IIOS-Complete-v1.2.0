"""Pure per-item decision logic: classify -> Kernel check -> policy rule.

No I/O, no ports, no wall clock — deterministic given
(items, kernel_invariants, policy_bundle, governance_available). This
is what makes "deterministic replay of decision" testable: call this
twice with the same inputs, get byte-identical outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from iios_governance.domain.action_classifier import classify_item, overall_class
from iios_governance.domain.models import ActionClass, ActionItem, DecisionOutcome, ItemDecision
from iios_governance.domain.policy_engine import evaluate_item
from iios_governance.domain.reason_codes import GOVERNANCE_UNAVAILABLE


@dataclass(frozen=True)
class PipelineResult:
    item_decisions: tuple[ItemDecision, ...]
    overall_decision: DecisionOutcome


def evaluate_items(
    items: tuple[ActionItem, ...],
    kernel_invariants: list[dict[str, Any]],
    policy_bundle: dict[str, Any],
    *,
    governance_available: bool,
) -> PipelineResult:
    decisions: list[ItemDecision] = []
    for item in items:
        classification = classify_item(item)
        evaluation = evaluate_item(item, classification, kernel_invariants, policy_bundle)

        outcome = evaluation.outcome
        reason_codes = evaluation.reason_codes

        if not governance_available:
            # Fail-closed rule (docs/03_GOVERNANCE_SECURITY.md), applied per item:
            # Class A may continue ONLY under a rule explicitly marked
            # offline_read_allowed; everything else denies.
            if not (
                classification.action_class == ActionClass.A
                and outcome == DecisionOutcome.ALLOW
                and evaluation.offline_read_allowed
            ):
                outcome = DecisionOutcome.DENY
                reason_codes = (GOVERNANCE_UNAVAILABLE,)

        decisions.append(
            ItemDecision(
                item_id=item.item_id,
                action_class=classification.action_class,
                outcome=outcome,
                reason_codes=reason_codes,
                matched_invariants=evaluation.matched_invariants,
                matched_rules=evaluation.matched_rules,
            )
        )

    strictest = DecisionOutcome.ALLOW
    for d in decisions:
        if d.outcome.strictness > strictest.strictness:
            strictest = d.outcome

    return PipelineResult(item_decisions=tuple(decisions), overall_decision=strictest)


__all__ = ["PipelineResult", "evaluate_items", "classify_item", "overall_class"]
