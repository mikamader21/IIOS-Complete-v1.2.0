"""An invalid action-request must produce a reproducible denial, never
an unhandled exception (docs/21_GOVERNANCE_CORE_SPEC.md — 'Action
Request Validation')."""

from __future__ import annotations

from iios_governance.domain.models import DecisionOutcome
from iios_governance.domain.reason_codes import SCHEMA_INVALID
from tests.governance.conftest import make_action_request


def test_valid_request_passes_schema(service_factory):
    service = service_factory()
    decision = service.evaluate(make_action_request(verb="read", resource_type="prop_firm_account"))
    assert decision.overall_decision == DecisionOutcome.ALLOW


def test_missing_required_field_denies_reproducibly(service_factory):
    service = service_factory()
    raw = make_action_request(verb="read", resource_type="prop_firm_account")
    del raw["correlation_id"]

    decision = service.evaluate(raw)

    assert decision.overall_decision == DecisionOutcome.DENY
    assert SCHEMA_INVALID in decision.reason_codes
    assert decision.fail_closed is True


def test_wrong_type_field_denies_reproducibly(service_factory):
    service = service_factory()
    raw = make_action_request(verb="read", resource_type="prop_firm_account")
    raw["items"] = "not-a-list"

    decision = service.evaluate(raw)

    assert decision.overall_decision == DecisionOutcome.DENY
    assert SCHEMA_INVALID in decision.reason_codes


def test_empty_items_denies_reproducibly(service_factory):
    service = service_factory()
    raw = make_action_request(verb="read", resource_type="prop_firm_account")
    raw["items"] = []

    decision = service.evaluate(raw)

    assert decision.overall_decision == DecisionOutcome.DENY
    assert SCHEMA_INVALID in decision.reason_codes


def test_malformed_request_never_raises(service_factory):
    service = service_factory()
    # A pathologically malformed instance — must still return a
    # PolicyDecision, never propagate an exception to the caller.
    decision = service.evaluate({"garbage": True})
    assert decision.overall_decision == DecisionOutcome.DENY
    assert SCHEMA_INVALID in decision.reason_codes
