from __future__ import annotations

import json
from pathlib import Path

import pytest

from iios_governance.adapters.filesystem.filesystem_policy_repository import (
    FilesystemPolicyRepository,
)
from iios_governance.domain.action_classifier import classify_item
from iios_governance.domain.errors import (
    PolicyBundleChecksumMismatchError,
    PolicyBundleInvalidError,
    PolicyBundleUnavailableError,
)
from iios_governance.domain.models import ActionItem, DecisionOutcome
from iios_governance.domain.policy_engine import evaluate_item


def test_real_mvp_bundle_loads_and_validates(
    real_policy_repository: FilesystemPolicyRepository,
) -> None:
    bundle = real_policy_repository.load_active_bundle()
    assert bundle["default_decision"] == "deny"
    assert bundle["rules"]


def test_missing_bundle_fails_closed(tmp_path: Path, repo_root: Path) -> None:
    repo = FilesystemPolicyRepository(
        tmp_path / "nope", repo_root / "governance" / "schemas" / "policy-bundle.schema.json"
    )
    with pytest.raises(PolicyBundleUnavailableError):
        repo.load_active_bundle()


def test_tampered_bundle_fails_closed(
    tmp_path: Path, real_policy_repository: FilesystemPolicyRepository, repo_root: Path
) -> None:
    bundle = real_policy_repository.load_active_bundle()
    bundle_dir = tmp_path / "mvp"
    bundle_dir.mkdir()
    tampered = dict(bundle)
    tampered["rules"] = [*bundle["rules"]]
    tampered["rules"][0] = {**tampered["rules"][0], "effect": "allow", "action_class": "D"}
    (bundle_dir / "policy.json").write_text(json.dumps(tampered), encoding="utf-8")
    (bundle_dir / "manifest.json").write_text(json.dumps({"sha256": "0" * 64}), encoding="utf-8")
    repo = FilesystemPolicyRepository(
        bundle_dir, repo_root / "governance" / "schemas" / "policy-bundle.schema.json"
    )
    with pytest.raises(PolicyBundleChecksumMismatchError):
        repo.load_active_bundle()


def test_bundle_malformed_json_fails_closed(tmp_path: Path, repo_root: Path) -> None:
    bundle_dir = tmp_path / "malformed"
    bundle_dir.mkdir()
    (bundle_dir / "policy.json").write_text("{not valid", encoding="utf-8")
    (bundle_dir / "manifest.json").write_text('{"sha256": "x"}', encoding="utf-8")
    repo = FilesystemPolicyRepository(
        bundle_dir, repo_root / "governance" / "schemas" / "policy-bundle.schema.json"
    )
    with pytest.raises(PolicyBundleUnavailableError):
        repo.load_active_bundle()


def test_bundle_exceeding_max_rules_rejected(tmp_path: Path, repo_root: Path) -> None:
    import hashlib

    bundle_dir = tmp_path / "too-many-rules"
    bundle_dir.mkdir()
    rule_template = {
        "match": {"verb": "read", "resource_type": "x", "environment": "*"},
        "action_class": "A",
        "effect": "allow",
        "precedence": 1,
    }
    bundle = {
        "schema_version": "1.0.0",
        "policy_version": "test",
        "default_decision": "deny",
        "limits": {"max_rules": 2},
        "rules": [{**rule_template, "id": f"POL-{i}"} for i in range(3)],
    }
    raw = json.dumps(bundle).encode("utf-8")
    (bundle_dir / "policy.json").write_bytes(raw)
    (bundle_dir / "manifest.json").write_text(
        json.dumps({"sha256": hashlib.sha256(raw).hexdigest()}), encoding="utf-8"
    )
    repo = FilesystemPolicyRepository(
        bundle_dir, repo_root / "governance" / "schemas" / "policy-bundle.schema.json"
    )
    with pytest.raises(PolicyBundleInvalidError):
        repo.load_active_bundle()


def test_invalid_bundle_shape_rejected(tmp_path: Path, repo_root: Path) -> None:
    bundle_dir = tmp_path / "invalid"
    bundle_dir.mkdir()
    bad_bundle = {
        "schema_version": "1.0.0",
        "policy_version": "x",
        "default_decision": "allow",
        "rules": [],
    }
    raw = json.dumps(bad_bundle).encode("utf-8")
    (bundle_dir / "policy.json").write_bytes(raw)
    import hashlib

    checksum = hashlib.sha256(raw).hexdigest()
    (bundle_dir / "manifest.json").write_text(json.dumps({"sha256": checksum}), encoding="utf-8")
    repo = FilesystemPolicyRepository(
        bundle_dir, repo_root / "governance" / "schemas" / "policy-bundle.schema.json"
    )
    with pytest.raises(PolicyBundleInvalidError):
        repo.load_active_bundle()


def test_deny_by_default_when_no_rule_matches(mvp_policy_bundle: dict) -> None:
    item = ActionItem(
        item_id="i1",
        verb="teleport",
        resource_type="spaceship",
        resource_ref="r",
        environment="staging",
    )
    classification = classify_item(item)
    evaluation = evaluate_item(item, classification, [], mvp_policy_bundle)
    assert evaluation.outcome == DecisionOutcome.DENY


def test_conflict_resolves_to_stricter_effect(mvp_policy_bundle: dict) -> None:
    # Two equally-specific, equal-precedence rules disagreeing must
    # resolve to the stricter effect, never allow.
    bundle = dict(mvp_policy_bundle)
    bundle["rules"] = [
        {
            "id": "POL-TEST-ALLOW",
            "match": {"verb": "test_verb", "resource_type": "test_res", "environment": "*"},
            "action_class": "B",
            "effect": "allow",
            "precedence": 50,
        },
        {
            "id": "POL-TEST-DENY",
            "match": {"verb": "test_verb", "resource_type": "test_res", "environment": "*"},
            "action_class": "B",
            "effect": "deny",
            "precedence": 50,
        },
    ]
    item = ActionItem(
        item_id="i1",
        verb="test_verb",
        resource_type="test_res",
        resource_ref="r",
        environment="staging",
    )
    classification = classify_item(item)
    evaluation = evaluate_item(item, classification, [], bundle)
    assert evaluation.outcome == DecisionOutcome.DENY


def test_exact_match_beats_wildcard(mvp_policy_bundle: dict) -> None:
    # Use an item the classifier already resolves to Class A (prop_firm_account
    # read) so evaluate_item reaches rule matching rather than short-circuiting
    # on UNCLASSIFIED_RESOURCE — the classifier and the policy bundle are
    # deliberately separate concerns (see domain/action_classifier.py).
    bundle = dict(mvp_policy_bundle)
    bundle["rules"] = [
        {
            "id": "POL-WILDCARD",
            "match": {"verb": "*", "resource_type": "prop_firm_account", "environment": "*"},
            "action_class": "C",
            "effect": "require_approval",
            "precedence": 10,
        },
        {
            "id": "POL-EXACT",
            "match": {
                "verb": "read",
                "resource_type": "prop_firm_account",
                "environment": "staging",
            },
            "action_class": "A",
            "effect": "allow",
            "precedence": 10,
            "offline_read_allowed": True,
        },
    ]
    item = ActionItem(
        item_id="i1",
        verb="read",
        resource_type="prop_firm_account",
        resource_ref="r",
        environment="staging",
    )
    classification = classify_item(item)
    evaluation = evaluate_item(item, classification, [], bundle)
    assert evaluation.outcome == DecisionOutcome.ALLOW
    assert evaluation.matched_rules == ("POL-EXACT",)


def test_kernel_short_circuits_policy_evaluation(mvp_policy_bundle: dict) -> None:
    bundle = dict(mvp_policy_bundle)
    bundle["rules"] = [
        {
            "id": "POL-WOULD-ALLOW-TRADE",
            "match": {"verb": "open", "resource_type": "trade_order", "environment": "*"},
            "action_class": "D",
            "effect": "allow",  # a misconfigured rule attempting to override the Kernel
            "precedence": 1000,
        }
    ]
    item = ActionItem(
        item_id="i1",
        verb="open",
        resource_type="trade_order",
        resource_ref="r",
        environment="staging",
    )
    classification = classify_item(item)
    evaluation = evaluate_item(item, classification, [], bundle)
    # Kernel check happens in policy_engine.evaluate_item BEFORE any rule
    # lookup for categorically-denied items — the misconfigured allow rule
    # is never even consulted.
    assert evaluation.outcome == DecisionOutcome.DENY
