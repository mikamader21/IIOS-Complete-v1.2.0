"""The 20 mandatory decision cases from docs/21_GOVERNANCE_CORE_SPEC.md,
exercised end-to-end through GovernanceService.evaluate()."""

from __future__ import annotations

from iios_governance.domain.models import DecisionOutcome
from iios_governance.domain.reason_codes import (
    APPROVAL_REQUIRED,
    CLASS_D_PROHIBITED,
    GOVERNANCE_MEDIATION_UNAVAILABLE,
    PROTECTED_AUTHORITY_PATH,
    SECRET_REFERENCE_APPROVAL_REQUIRED,
    SECRET_VALUE_DISCLOSURE_FORBIDDEN,
)
from tests.governance.conftest import make_action_request


# 1. Read prop-firm account balance -> A, allow.
def test_case_01_read_prop_firm_balance(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="read", resource_type="prop_firm_account")
    )
    assert decision.overall_decision == DecisionOutcome.ALLOW
    assert decision.item_decisions[0].action_class.value == "A"


# 2. Calculate drawdown -> A, allow.
def test_case_02_calculate_drawdown(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="compute", resource_type="drawdown_calculation")
    )
    assert decision.overall_decision == DecisionOutcome.ALLOW


# 3. Open a trade order -> D, deny.
def test_case_03_open_trade_order(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="open", resource_type="trade_order")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].action_class.value == "D"
    assert CLASS_D_PROHIBITED in decision.item_decisions[0].reason_codes


# 4. Modify a stop loss (order modification) -> D, deny.
def test_case_04_modify_stop_loss(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="modify_order", resource_type="trade_order")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].action_class.value == "D"


# 5. Withdraw capital -> D, deny.
def test_case_05_withdraw_capital(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="withdraw", resource_type="capital")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].action_class.value == "D"


# 6. Create a Git branch -> B, allow.
def test_case_06_create_git_branch(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="create", resource_type="git_branch")
    )
    assert decision.overall_decision == DecisionOutcome.ALLOW
    assert decision.item_decisions[0].action_class.value == "B"


# 7. Edit code on a feature branch -> B, allow.
def test_case_07_edit_code(service_factory):
    decision = service_factory().evaluate(make_action_request(verb="edit", resource_type="code"))
    assert decision.overall_decision == DecisionOutcome.ALLOW
    assert decision.item_decisions[0].action_class.value == "B"


# 8. Merge to main -> C, require_approval.
def test_case_08_merge_protected_branch(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="merge", resource_type="git_protected_branch")
    )
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL
    assert decision.item_decisions[0].action_class.value == "C"
    assert decision.item_decisions[0].approval_id is not None
    assert APPROVAL_REQUIRED in decision.item_decisions[0].reason_codes


# 9. Deploy to production -> C, require_approval.
def test_case_09_deploy_production(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="deploy", resource_type="production_target")
    )
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL
    assert decision.item_decisions[0].approval_id is not None


# 10a. secret_value.read -> D, deny, unconditional (no approval can authorize it).
def test_case_10a_secret_value_read_is_forbidden(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="secret_value.read", resource_type="secret")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].action_class.value == "D"
    assert SECRET_VALUE_DISCLOSURE_FORBIDDEN in decision.item_decisions[0].reason_codes
    assert decision.item_decisions[0].approval_id is None


# 10b. secret_reference.use -> C, require_approval.
def test_case_10b_secret_reference_use_requires_approval(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="secret_reference.use", resource_type="secret")
    )
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL
    assert decision.item_decisions[0].action_class.value == "C"
    assert SECRET_REFERENCE_APPROVAL_REQUIRED in decision.item_decisions[0].reason_codes


# 11. Rotate an API key -> C, require_approval.
def test_case_11_rotate_api_key(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="rotate", resource_type="api_key")
    )
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL


# 12. Activate an MCP connector -> C, require_approval.
def test_case_12_activate_mcp_connector(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="activate", resource_type="mcp_connector")
    )
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL


# 13. Send an email -> C, require_approval.
def test_case_13_send_email(service_factory):
    decision = service_factory().evaluate(make_action_request(verb="send", resource_type="email"))
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL


# 14. Make.com list/query metadata (read-only, allowlisted) -> A, allow.
def test_case_14_make_metadata_read(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="list", resource_type="make_scenario_metadata")
    )
    assert decision.overall_decision == DecisionOutcome.ALLOW
    assert decision.item_decisions[0].action_class.value == "A"


# 14b. Make.com mutation -> C, but denied today (no live Governance mediation).
def test_case_14b_make_mutation_denied(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="run", resource_type="make_scenario")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].action_class.value == "C"
    assert GOVERNANCE_MEDIATION_UNAVAILABLE in decision.item_decisions[0].reason_codes


# 15. Migrate Supabase schema -> C, require_approval.
def test_case_15_migrate_supabase_schema(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="migrate", resource_type="supabase_schema")
    )
    assert decision.overall_decision == DecisionOutcome.REQUIRE_APPROVAL


# 16. Modify the Constitution -> D, deny, categorically outside authorization surface.
def test_case_16_modify_constitution(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="modify", resource_type="constitution")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert PROTECTED_AUTHORITY_PATH in decision.item_decisions[0].reason_codes
    assert decision.item_decisions[0].approval_id is None


# 17. Modify the Invariant Kernel -> D, deny, categorically outside authorization surface.
def test_case_17_modify_invariant_kernel(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="modify", resource_type="invariant_kernel")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert PROTECTED_AUTHORITY_PATH in decision.item_decisions[0].reason_codes


# 18. Delete an audit record -> D, deny.
def test_case_18_delete_audit_record(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="delete", resource_type="audit_record")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].action_class.value == "D"


# 19. Budget overspend -> deny for further requests in scope.
def test_case_19_budget_exceeded(service_factory, budget_tracker):
    budget_tracker.mark_exceeded("trading:ict-analysis:task-1")
    service = service_factory()
    raw = make_action_request(verb="read", resource_type="prop_firm_account")
    raw["budget_context"] = {"domain": "trading", "profile": "ict-analysis", "task_id": "task-1"}
    decision = service.evaluate(raw)
    assert decision.overall_decision == DecisionOutcome.DENY
    assert "BUDGET_EXCEEDED" in decision.reason_codes


# 20. Governance unavailable -> deny for B/C/D; A only under cached offline policy.
def test_case_20_governance_unavailable_denies_b(service_factory):
    service = service_factory(governance_available=False)
    decision = service.evaluate(make_action_request(verb="create", resource_type="git_branch"))
    assert decision.overall_decision == DecisionOutcome.DENY
    assert "GOVERNANCE_UNAVAILABLE" in decision.item_decisions[0].reason_codes


def test_case_20_governance_unavailable_allows_cached_class_a(service_factory):
    service = service_factory(governance_available=False)
    decision = service.evaluate(make_action_request(verb="read", resource_type="prop_firm_account"))
    assert decision.overall_decision == DecisionOutcome.ALLOW


def test_case_20_governance_unavailable_denies_class_a_without_offline_flag(service_factory):
    service = service_factory(governance_available=False)
    # drawdown_calculation IS offline_read_allowed in the MVP bundle;
    # use an item whose class is A only via the unclassified fallback,
    # which never carries offline_read_allowed.
    decision = service.evaluate(
        make_action_request(verb="unknown_verb", resource_type="unknown_resource")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
