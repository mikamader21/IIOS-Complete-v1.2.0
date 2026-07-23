"""End-to-end GovernanceService scenarios beyond the 20 mandatory cases:
deny-by-default, ambiguous classification, multiple items, duplicate
request/idempotency, audit unavailable, Kernel/policy tampering, kill
switch, and deterministic replay."""

from __future__ import annotations

import copy

from iios_governance.adapters.filesystem.filesystem_kernel_repository import (
    FilesystemKernelRepository,
)
from iios_governance.adapters.filesystem.filesystem_policy_repository import (
    FilesystemPolicyRepository,
)
from iios_governance.domain.models import DecisionOutcome
from iios_governance.domain.reason_codes import (
    AUDIT_UNAVAILABLE,
    KERNEL_CHECKSUM_MISMATCH,
    KILL_SWITCH_ACTIVE,
    POLICY_BUNDLE_UNAVAILABLE,
    UNCLASSIFIED_RESOURCE,
)
from tests.governance.conftest import make_action_request


def test_deny_by_default_for_unmatched_action(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="teleport", resource_type="spaceship")
    )
    assert decision.overall_decision == DecisionOutcome.DENY


def test_ambiguous_classification_never_resolves_to_allow(service_factory):
    decision = service_factory().evaluate(
        make_action_request(verb="frobnicate", resource_type="mystery_widget")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert UNCLASSIFIED_RESOURCE in decision.item_decisions[0].reason_codes


def test_multiple_items_overall_class_is_strictest(service_factory):
    raw = make_action_request(verb="read", resource_type="prop_firm_account")
    raw["items"].append(
        {
            "item_id": "item-2",
            "verb": "open",
            "resource_type": "trade_order",
            "resource_ref": "r2",
            "environment": "staging",
        }
    )
    decision = service_factory().evaluate(raw)
    assert decision.overall_decision == DecisionOutcome.DENY
    assert decision.item_decisions[0].outcome == DecisionOutcome.ALLOW
    assert decision.item_decisions[1].outcome == DecisionOutcome.DENY


def test_multiple_items_each_classified_independently(service_factory):
    raw = make_action_request(verb="create", resource_type="git_branch")
    raw["items"].append(
        {
            "item_id": "item-2",
            "verb": "merge",
            "resource_type": "git_protected_branch",
            "resource_ref": "r2",
            "environment": "staging",
        }
    )
    decision = service_factory().evaluate(raw)
    assert len(decision.item_decisions) == 2
    assert decision.item_decisions[0].action_class.value == "B"
    assert decision.item_decisions[1].action_class.value == "C"


def test_duplicate_request_replays_original_decision(service_factory):
    service = service_factory()
    raw = make_action_request(
        verb="read", resource_type="prop_firm_account", idempotency_key="fixed-key-1"
    )

    first = service.evaluate(raw)
    assert first.replayed is False

    second = service.evaluate(copy.deepcopy(raw))
    assert second.replayed is True
    assert second.decision_id == first.decision_id
    assert second.overall_decision == first.overall_decision


def test_idempotency_scoped_to_actor_action_resource_environment(service_factory):
    service = service_factory()
    raw1 = make_action_request(
        verb="read", resource_type="prop_firm_account", idempotency_key="key-a", actor_id="actor-1"
    )
    raw2 = make_action_request(
        verb="read", resource_type="prop_firm_account", idempotency_key="key-a", actor_id="actor-2"
    )
    d1 = service.evaluate(raw1)
    d2 = service.evaluate(raw2)
    assert d1.decision_id != d2.decision_id
    assert d2.replayed is False


def test_audit_unavailable_forces_deny_on_would_be_allow(service_factory):
    service = service_factory(audit_available=False)
    decision = service.evaluate(make_action_request(verb="read", resource_type="prop_firm_account"))
    assert decision.overall_decision == DecisionOutcome.DENY
    assert AUDIT_UNAVAILABLE in decision.reason_codes
    assert decision.fail_closed is True


def test_audit_unavailable_does_not_change_an_already_denied_decision(service_factory):
    service = service_factory(audit_available=False)
    decision = service.evaluate(make_action_request(verb="open", resource_type="trade_order"))
    assert decision.overall_decision == DecisionOutcome.DENY


def test_kernel_altered_denies_everything(
    tmp_path,
    service_factory,
    real_kernel_repository,
    in_memory_policy_repository,
    action_request_schema,
    clock,
    audit_chain,
    approval_service,
    kill_switch,
    idempotency_store,
    budget_tracker,
):
    import json

    invariants, checksum = real_kernel_repository.load_verified_kernel()
    kernel_dir = tmp_path / "tampered-kernel"
    kernel_dir.mkdir()
    tampered = dict(invariants)
    tampered["invariants"] = [
        *invariants["invariants"],
        {"id": "INV-999", "statement": "x", "enforcement": "y"},
    ]
    (kernel_dir / "invariants.json").write_text(json.dumps(tampered), encoding="utf-8")
    (kernel_dir / "manifest.json").write_text(json.dumps({"sha256": checksum}), encoding="utf-8")

    from tests.governance.conftest import build_service

    service = build_service(
        kernel_repository=FilesystemKernelRepository(kernel_dir),
        policy_repository=in_memory_policy_repository,
        action_request_schema=action_request_schema,
        clock=clock,
        audit_chain=audit_chain,
        approval_service=approval_service,
        kill_switch=kill_switch,
        idempotency_store=idempotency_store,
        budget_tracker=budget_tracker,
    )
    decision = service.evaluate(make_action_request(verb="read", resource_type="prop_firm_account"))
    assert decision.overall_decision == DecisionOutcome.DENY
    assert KERNEL_CHECKSUM_MISMATCH in decision.item_decisions[0].reason_codes
    assert decision.fail_closed is True


def test_policy_bundle_unavailable_denies_everything(
    tmp_path,
    service_factory,
    real_kernel_repository,
    action_request_schema,
    clock,
    audit_chain,
    approval_service,
    kill_switch,
    idempotency_store,
    budget_tracker,
    repo_root,
):
    from tests.governance.conftest import build_service

    broken_policy_repo = FilesystemPolicyRepository(
        tmp_path / "does-not-exist",
        repo_root / "governance" / "schemas" / "policy-bundle.schema.json",
    )
    service = build_service(
        kernel_repository=real_kernel_repository,
        policy_repository=broken_policy_repo,
        action_request_schema=action_request_schema,
        clock=clock,
        audit_chain=audit_chain,
        approval_service=approval_service,
        kill_switch=kill_switch,
        idempotency_store=idempotency_store,
        budget_tracker=budget_tracker,
    )
    decision = service.evaluate(make_action_request(verb="read", resource_type="prop_firm_account"))
    assert decision.overall_decision == DecisionOutcome.DENY
    assert POLICY_BUNDLE_UNAVAILABLE in decision.item_decisions[0].reason_codes


def test_kill_switch_active_denies_matching_scope(service_factory, kill_switch, clock):
    kill_switch.activate(
        level="L2",
        scope_type="actor",
        scope_ref="actor-1",
        actor="owner",
        auth_method="owner_session",
        reason="test",
        now_iso=clock.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    service = service_factory()
    decision = service.evaluate(
        make_action_request(verb="read", resource_type="prop_firm_account", actor_id="actor-1")
    )
    assert decision.overall_decision == DecisionOutcome.DENY
    assert KILL_SWITCH_ACTIVE in decision.item_decisions[0].reason_codes


def test_kill_switch_l3_blocks_every_actor(service_factory, kill_switch, clock):
    kill_switch.activate(
        level="L3",
        scope_type="all_workers",
        scope_ref=None,
        actor="owner",
        auth_method="owner_session",
        reason="systemic issue",
        now_iso=clock.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    service = service_factory()
    decision = service.evaluate(
        make_action_request(verb="read", resource_type="prop_firm_account", actor_id="any-actor")
    )
    assert decision.overall_decision == DecisionOutcome.DENY


def test_deterministic_replay_of_decision_produces_same_content(service_factory):
    service1 = service_factory()
    service2 = service_factory()
    raw = make_action_request(
        verb="merge", resource_type="git_protected_branch", idempotency_key="k1"
    )

    d1 = service1.evaluate(copy.deepcopy(raw))
    d2 = service2.evaluate(
        copy.deepcopy({**raw, "request_id": raw["request_id"], "idempotency_key": "k2-different"})
    )

    # Different idempotency_key => genuinely re-evaluated, not replayed
    # from cache — and still produces the SAME classification/decision
    # content because the pipeline is a pure function of its inputs.
    assert d2.replayed is False
    assert d1.overall_decision == d2.overall_decision
    assert [d.action_class for d in d1.item_decisions] == [
        d.action_class for d in d2.item_decisions
    ]
    assert [d.outcome for d in d1.item_decisions] == [d.outcome for d in d2.item_decisions]
