"""Deterministic Action Classifier.

docs/21_GOVERNANCE_CORE_SPEC.md — "B. Action Classifier":
  - the final class is NEVER decided by an LLM or by `classifier_hint`;
  - ambiguous classification resolves to the strictest applicable class;
  - unknown resource types never resolve to A.

This module is a pure function of (verb, resource_type, environment) —
no I/O, no randomness, no wall-clock read, so it is trivially
deterministic and replayable.
"""

from __future__ import annotations

from dataclasses import dataclass

from iios_governance.domain.models import ActionClass, ActionItem
from iios_governance.domain.reason_codes import UNCLASSIFIED_RESOURCE

# Resource types that are categorically outside Governance's authorization
# surface (Constitution Article III.1; docs/21 cases #16/#17/#18). No rule,
# no approval, and no capability can ever move these off Class D.
_PROTECTED_AUTHORITY_RESOURCE_TYPES = frozenset(
    {"constitution", "master_charter", "invariant_kernel", "audit_record", "audit_log"}
)

# verb -> forced Class D when it appears with ANY resource_type (Constitution
# Article IV-D / INV-002 financial-write prohibition).
_FINANCIAL_WRITE_VERBS = frozenset(
    {"open", "modify_order", "close_order", "withdraw", "transfer", "purchase", "pay"}
)

_FINANCIAL_RESOURCE_TYPES = frozenset({"trade_order", "capital", "payment"})

# Exact (verb, resource_type) -> ActionClass table. This is the
# authoritative source; docs/21_GOVERNANCE_CORE_SPEC.md's 20-case matrix
# is the human-readable mirror of this table, not the other way around —
# a mismatch between the two is a defect in one of them.
_CLASS_TABLE: dict[tuple[str, str], ActionClass] = {
    ("read", "prop_firm_account"): ActionClass.A,
    ("compute", "drawdown_calculation"): ActionClass.A,
    ("query", "vault_note"): ActionClass.A,
    ("list", "make_scenario_metadata"): ActionClass.A,
    ("query", "make_scenario_metadata"): ActionClass.A,
    ("create", "git_branch"): ActionClass.B,
    ("edit", "code"): ActionClass.B,
    ("merge", "git_protected_branch"): ActionClass.C,
    ("deploy", "production_target"): ActionClass.C,
    ("secret_reference.use", "secret"): ActionClass.C,
    ("secret_reference.use", "api_key"): ActionClass.C,
    ("rotate", "api_key"): ActionClass.C,
    ("activate", "mcp_connector"): ActionClass.C,
    ("send", "email"): ActionClass.C,
    ("run", "make_scenario"): ActionClass.C,
    ("activate", "make_scenario"): ActionClass.C,
    ("deactivate", "make_scenario"): ActionClass.C,
    ("edit", "make_scenario"): ActionClass.C,
    ("create", "make_scenario"): ActionClass.C,
    ("migrate", "supabase_schema"): ActionClass.C,
    ("open", "trade_order"): ActionClass.D,
    ("modify_order", "trade_order"): ActionClass.D,
    ("close_order", "trade_order"): ActionClass.D,
    ("withdraw", "capital"): ActionClass.D,
    ("secret_value.read", "secret"): ActionClass.D,
}


@dataclass(frozen=True)
class ClassificationResult:
    action_class: ActionClass
    reason_codes: tuple[str, ...]
    is_protected_authority: bool = False


def classify_item(item: ActionItem) -> ClassificationResult:
    """Classify a single ActionItem. Never consults classifier_hint —
    that field does not even reach this function (see
    application/decision_pipeline.py)."""

    # 1. Categorical exclusions — no table lookup can override these.
    if item.resource_type in _PROTECTED_AUTHORITY_RESOURCE_TYPES:
        return ClassificationResult(
            ActionClass.D, reason_codes=("PROTECTED_AUTHORITY_PATH",), is_protected_authority=True
        )
    if item.verb == "secret_value.read":
        return ClassificationResult(
            ActionClass.D, reason_codes=("SECRET_VALUE_DISCLOSURE_FORBIDDEN",)
        )
    if item.verb in _FINANCIAL_WRITE_VERBS or item.resource_type in _FINANCIAL_RESOURCE_TYPES:
        return ClassificationResult(ActionClass.D, reason_codes=("CLASS_D_PROHIBITED",))

    # 2. Exact table match.
    key = (item.verb, item.resource_type)
    if key in _CLASS_TABLE:
        return ClassificationResult(_CLASS_TABLE[key], reason_codes=())

    # 3. Unmatched — strictest-applicable-class rule. Never A.
    write_like = item.verb not in {"read", "query", "list", "compute", "get"}
    action_class = ActionClass.C if write_like else ActionClass.C
    return ClassificationResult(action_class, reason_codes=(UNCLASSIFIED_RESOURCE,))


def overall_class(item_classes: tuple[ActionClass, ...]) -> ActionClass:
    """The request-level class is the maximum (strictest) across items."""
    strictest = ActionClass.A
    for c in item_classes:
        if c.is_stricter_than(strictest):
            strictest = c
    return strictest
