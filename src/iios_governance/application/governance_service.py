"""GovernanceService.evaluate(action_request) -> PolicyDecision.

Governance decides. Governance never executes the requested action —
there is no method on this class that calls out to any external
system; `evaluate` only ever returns a decision plus audit events.

Pipeline (docs/21_GOVERNANCE_CORE_SPEC.md):
  schema validation -> idempotency check -> Kernel load/verify ->
  kill switch check -> budget check -> policy bundle load/verify ->
  per-item classify+Kernel+policy (application/decision_pipeline.py) ->
  approval requirement -> audit event -> decision.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from jsonschema.validators import Draft202012Validator

from iios_governance.application.decision_pipeline import evaluate_items
from iios_governance.domain.action_classifier import classify_item
from iios_governance.domain.approval_service import ApprovalService
from iios_governance.domain.audit_chain import AuditChain
from iios_governance.domain.errors import (
    KernelChecksumMismatchError,
    KernelUnavailableError,
    PolicyBundleChecksumMismatchError,
    PolicyBundleInvalidError,
    PolicyBundleUnavailableError,
)
from iios_governance.domain.kill_switch import KillSwitch
from iios_governance.domain.models import (
    ActionItem,
    ActionRequest,
    Actor,
    DecisionOutcome,
    ItemDecision,
    PolicyDecision,
)
from iios_governance.domain.reason_codes import (
    APPROVAL_REQUIRED,
    AUDIT_UNAVAILABLE,
    BUDGET_EXCEEDED,
    KERNEL_CHECKSUM_MISMATCH,
    KERNEL_UNAVAILABLE,
    KILL_SWITCH_ACTIVE,
    POLICY_BUNDLE_INVALID,
    POLICY_BUNDLE_UNAVAILABLE,
    SCHEMA_INVALID,
)
from iios_governance.ports.budget_tracker import BudgetTracker
from iios_governance.ports.clock import Clock
from iios_governance.ports.idempotency_store import IdempotencyStore
from iios_governance.ports.kernel_repository import KernelRepository
from iios_governance.ports.policy_repository import PolicyRepository

_ISO = "%Y-%m-%dT%H:%M:%SZ"
_APPROVAL_TTL_MINUTES = {"A": 0, "B": 0, "C": 15, "D": 0}  # ADR-0011 — Class C approvals


@dataclass
class GovernanceServiceConfig:
    governance_available: bool = True
    audit_available: bool = True


class GovernanceService:
    def __init__(
        self,
        *,
        kernel_repository: KernelRepository,
        policy_repository: PolicyRepository,
        action_request_schema: dict[str, Any],
        clock: Clock,
        audit_chain: AuditChain,
        approval_service: ApprovalService,
        kill_switch: KillSwitch,
        idempotency_store: IdempotencyStore,
        budget_tracker: BudgetTracker,
        config: GovernanceServiceConfig | None = None,
    ) -> None:
        self._kernel_repository = kernel_repository
        self._policy_repository = policy_repository
        self._request_validator = Draft202012Validator(action_request_schema)
        self._clock = clock
        self._audit = audit_chain
        self._approvals = approval_service
        self._kill_switch = kill_switch
        self._idempotency = idempotency_store
        self._budget = budget_tracker
        self.config = config or GovernanceServiceConfig()

    def evaluate(self, action_request_raw: dict[str, Any]) -> PolicyDecision:
        errors = [
            f"{list(e.path)}: {e.message}"
            for e in self._request_validator.iter_errors(action_request_raw)
        ]
        if errors:
            return self._deny_malformed(action_request_raw, errors)

        request = self._to_domain(action_request_raw)

        cache_scope = self._idempotency_scope(request)
        cached = self._idempotency.get(cache_scope)
        if cached is not None:
            return PolicyDecision(**{**cached.__dict__, "replayed": True})

        now = self._clock.now()

        kernel_invariants: list[dict[str, Any]] = []
        kernel_checksum = ""
        kernel_error: str | None = None
        try:
            kernel_invariants_dict, kernel_checksum = self._kernel_repository.load_verified_kernel()
            kernel_invariants = kernel_invariants_dict["invariants"]
        except KernelChecksumMismatchError:
            kernel_error = KERNEL_CHECKSUM_MISMATCH
        except KernelUnavailableError:
            kernel_error = KERNEL_UNAVAILABLE

        kill_level = self._kill_switch.is_blocking(
            scope_type="actor", scope_ref=request.actor.actor_id
        )

        budget_scope = self._budget_scope(request)
        budget_exceeded = budget_scope is not None and self._budget.is_exceeded(scope=budget_scope)

        policy_bundle: dict[str, Any] | None = None
        policy_error: str | None = None
        try:
            policy_bundle = self._policy_repository.load_active_bundle()
        except PolicyBundleChecksumMismatchError:
            policy_error = POLICY_BUNDLE_INVALID
        except (PolicyBundleUnavailableError, PolicyBundleInvalidError):
            policy_error = POLICY_BUNDLE_UNAVAILABLE

        if kernel_error or kill_level or budget_exceeded or policy_error:
            reason = (
                kernel_error
                or (KILL_SWITCH_ACTIVE if kill_level else None)
                or (BUDGET_EXCEEDED if budget_exceeded else None)
                or policy_error
            )
            assert reason is not None  # the enclosing `if` guarantees at least one is truthy
            item_decisions = tuple(
                ItemDecision(
                    item_id=item.item_id,
                    action_class=classify_item(item).action_class,
                    outcome=DecisionOutcome.DENY,
                    reason_codes=(reason,),
                )
                for item in request.items
            )
            decision = self._finalize(
                request,
                item_decisions,
                DecisionOutcome.DENY,
                now,
                kernel_checksum,
                fail_closed=True,
                reason_codes=(reason,),
            )
            self._idempotency.put(cache_scope, decision)
            return decision

        assert policy_bundle is not None
        result = evaluate_items(
            request.items,
            kernel_invariants,
            policy_bundle,
            governance_available=self.config.governance_available,
        )

        resolved_item_decisions: list[ItemDecision] = []
        for d in result.item_decisions:
            approval_id = None
            if d.outcome == DecisionOutcome.REQUIRE_APPROVAL:
                approval = self._approvals.request_approval(
                    request_id=request.request_id,
                    correlation_id=request.correlation_id,
                    requested_by=request.actor.actor_id,
                    ttl_minutes=_APPROVAL_TTL_MINUTES.get(d.action_class.value, 15) or 15,
                )
                approval_id = approval.approval_id
                if APPROVAL_REQUIRED not in d.reason_codes:
                    d = ItemDecision(
                        **{**d.__dict__, "reason_codes": (*d.reason_codes, APPROVAL_REQUIRED)}
                    )
            resolved_item_decisions.append(
                ItemDecision(**{**d.__dict__, "approval_id": approval_id})
            )

        decision = self._finalize(
            request,
            tuple(resolved_item_decisions),
            result.overall_decision,
            now,
            kernel_checksum,
            fail_closed=not self.config.governance_available,
        )

        if not self._try_audit(request, decision):
            if decision.overall_decision != DecisionOutcome.DENY:
                decision = PolicyDecision(
                    **{
                        **decision.__dict__,
                        "overall_decision": DecisionOutcome.DENY,
                        "reason_codes": (*decision.reason_codes, AUDIT_UNAVAILABLE),
                        "fail_closed": True,
                    }
                )

        self._idempotency.put(cache_scope, decision)
        return decision

    # -- helpers ------------------------------------------------------

    def _deny_malformed(self, raw: dict[str, Any], errors: list[str]) -> PolicyDecision:
        now = self._clock.now()
        request_id = raw.get("request_id") or str(uuid.uuid4())
        correlation_id = raw.get("correlation_id") or str(uuid.uuid4())
        return PolicyDecision(
            decision_id=str(uuid.uuid4()),
            request_id=request_id,
            correlation_id=correlation_id,
            idempotency_key=raw.get("idempotency_key", ""),
            policy_version="",
            kernel_checksum="",
            evaluated_at=now.strftime(_ISO),
            item_decisions=(),
            overall_decision=DecisionOutcome.DENY,
            reason_codes=(SCHEMA_INVALID,),
            explanation="; ".join(errors)[:2000],
            fail_closed=True,
        )

    def _to_domain(self, raw: dict[str, Any]) -> ActionRequest:
        actor_raw = raw["actor"]
        actor = Actor(
            actor_id=actor_raw["actor_id"],
            actor_type=actor_raw["actor_type"],
            auth_method=actor_raw["auth_method"],
            on_behalf_of=actor_raw.get("on_behalf_of"),
        )
        items = tuple(
            ActionItem(
                item_id=i["item_id"],
                verb=i["verb"],
                resource_type=i["resource_type"],
                resource_ref=i["resource_ref"],
                environment=i["environment"],
                reason=i.get("reason"),
                risk_signals=tuple(i.get("risk_signals", [])),
            )
            for i in raw["items"]
        )
        return ActionRequest(
            request_id=raw["request_id"],
            idempotency_key=raw["idempotency_key"],
            correlation_id=raw["correlation_id"],
            actor=actor,
            requested_at=raw["requested_at"],
            items=items,
            budget_context=raw.get("budget_context"),
            classifier_hint=raw.get("classifier_hint"),
            decomposable=raw.get("decomposable", False),
        )

    @staticmethod
    def _idempotency_scope(request: ActionRequest) -> str:
        return (
            f"{request.actor.actor_id}:{request.items[0].verb if request.items else ''}:"
            f"{request.items[0].resource_ref if request.items else ''}:"
            f"{request.items[0].environment if request.items else ''}:{request.idempotency_key}"
        )

    @staticmethod
    def _budget_scope(request: ActionRequest) -> str | None:
        if not request.budget_context:
            return None
        bc = request.budget_context
        return f"{bc.get('domain', '')}:{bc.get('profile', '')}:{bc.get('task_id', '')}"

    def _finalize(
        self,
        request: ActionRequest,
        item_decisions: tuple[ItemDecision, ...],
        overall: DecisionOutcome,
        now: datetime,
        kernel_checksum: str,
        *,
        fail_closed: bool,
        reason_codes: tuple[str, ...] = (),
    ) -> PolicyDecision:
        policy_version = ""
        try:
            policy_version = self._policy_repository.load_active_bundle().get("policy_version", "")
        except Exception:  # noqa: BLE001 - best-effort only, decision already computed
            pass
        return PolicyDecision(
            decision_id=str(uuid.uuid4()),
            request_id=request.request_id,
            correlation_id=request.correlation_id,
            idempotency_key=request.idempotency_key,
            policy_version=policy_version,
            kernel_checksum=kernel_checksum,
            evaluated_at=now.strftime(_ISO),
            item_decisions=item_decisions,
            overall_decision=overall,
            fail_closed=fail_closed,
            reason_codes=reason_codes,
        )

    def _try_audit(self, request: ActionRequest, decision: PolicyDecision) -> bool:
        if not self.config.audit_available:
            return False
        try:
            self._audit.append(
                partition=request.correlation_id,
                event_type="request_received",
                actor=request.actor.actor_id,
                correlation_id=request.correlation_id,
                request_id=request.request_id,
            )
            self._audit.append(
                partition=request.correlation_id,
                event_type="policy_decision",
                actor=request.actor.actor_id,
                correlation_id=request.correlation_id,
                request_id=request.request_id,
                policy_version=decision.policy_version,
                decision=decision.overall_decision.value,
                reason_codes=tuple(code for d in decision.item_decisions for code in d.reason_codes)
                or decision.reason_codes,
            )
            return True
        except Exception:  # noqa: BLE001 - any audit failure is treated uniformly
            return False
