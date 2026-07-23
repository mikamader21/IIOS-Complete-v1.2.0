from __future__ import annotations

import pytest

from iios_governance.domain.action_classifier import classify_item, overall_class
from iios_governance.domain.models import ActionClass, ActionItem
from iios_governance.domain.reason_codes import UNCLASSIFIED_RESOURCE


def _item(verb: str, resource_type: str, environment: str = "staging") -> ActionItem:
    return ActionItem(
        item_id="i1",
        verb=verb,
        resource_type=resource_type,
        resource_ref="r",
        environment=environment,
    )


@pytest.mark.parametrize(
    ("verb", "resource_type", "expected"),
    [
        ("read", "prop_firm_account", ActionClass.A),
        ("compute", "drawdown_calculation", ActionClass.A),
        ("list", "make_scenario_metadata", ActionClass.A),
        ("create", "git_branch", ActionClass.B),
        ("edit", "code", ActionClass.B),
        ("merge", "git_protected_branch", ActionClass.C),
        ("deploy", "production_target", ActionClass.C),
        ("secret_reference.use", "secret", ActionClass.C),
        ("rotate", "api_key", ActionClass.C),
        ("migrate", "supabase_schema", ActionClass.C),
        ("run", "make_scenario", ActionClass.C),
        ("open", "trade_order", ActionClass.D),
        ("modify_order", "trade_order", ActionClass.D),
        ("close_order", "trade_order", ActionClass.D),
        ("withdraw", "capital", ActionClass.D),
        ("secret_value.read", "secret", ActionClass.D),
        ("modify", "constitution", ActionClass.D),
        ("modify", "invariant_kernel", ActionClass.D),
        ("delete", "audit_record", ActionClass.D),
    ],
)
def test_classification_table(verb: str, resource_type: str, expected: ActionClass) -> None:
    result = classify_item(_item(verb, resource_type))
    assert result.action_class == expected


def test_unknown_resource_never_resolves_to_a() -> None:
    result = classify_item(_item("frobnicate", "unknown_widget"))
    assert result.action_class != ActionClass.A
    assert UNCLASSIFIED_RESOURCE in result.reason_codes


def test_classifier_hint_is_never_authoritative() -> None:
    # classify_item's signature does not even accept a hint — this test
    # documents that fact structurally: constructing an ActionItem with
    # extra "hint-shaped" data has no effect because the field doesn't
    # exist on the domain model at all.
    item = _item("open", "trade_order")
    result = classify_item(item)
    assert result.action_class == ActionClass.D  # unaffected by any hint framing


def test_overall_class_is_strictest_across_items() -> None:
    classes = (ActionClass.A, ActionClass.B, ActionClass.D, ActionClass.C)
    assert overall_class(classes) == ActionClass.D


def test_overall_class_all_a_is_a() -> None:
    assert overall_class((ActionClass.A, ActionClass.A)) == ActionClass.A


def test_protected_authority_paths_are_categorical() -> None:
    for resource_type in ("constitution", "master_charter", "invariant_kernel", "audit_record"):
        result = classify_item(_item("modify", resource_type))
        assert result.action_class == ActionClass.D
        assert result.is_protected_authority is True
