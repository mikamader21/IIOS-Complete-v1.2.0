from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from iios_governance.adapters.filesystem.filesystem_kernel_repository import (
    FilesystemKernelRepository,
)
from iios_governance.adapters.filesystem.filesystem_policy_repository import (
    FilesystemPolicyRepository,
)
from iios_governance.adapters.memory.in_memory_approval_store import InMemoryApprovalStore
from iios_governance.adapters.memory.in_memory_audit_store import InMemoryAuditStore
from iios_governance.adapters.memory.in_memory_budget_tracker import InMemoryBudgetTracker
from iios_governance.adapters.memory.in_memory_capability_store import InMemoryCapabilityStore
from iios_governance.adapters.memory.in_memory_idempotency_store import InMemoryIdempotencyStore
from iios_governance.adapters.memory.in_memory_policy_repository import InMemoryPolicyRepository
from iios_governance.application.governance_service import (
    GovernanceService,
    GovernanceServiceConfig,
)
from iios_governance.domain.approval_service import ApprovalService
from iios_governance.domain.audit_chain import AuditChain
from iios_governance.domain.kill_switch import KillSwitch
from tests.governance.fakes import DeterministicTestCanonicalizer, FixedClock

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def schema(repo_root: Path):
    def _load(name: str) -> dict:
        return json.loads((repo_root / "governance" / "schemas" / name).read_text(encoding="utf-8"))

    return _load


@pytest.fixture
def real_kernel_repository(repo_root: Path) -> FilesystemKernelRepository:
    return FilesystemKernelRepository(repo_root / "governance" / "invariant-kernel")


@pytest.fixture
def real_policy_repository(repo_root: Path) -> FilesystemPolicyRepository:
    return FilesystemPolicyRepository(
        repo_root / "governance" / "policy-bundles" / "mvp",
        repo_root / "governance" / "schemas" / "policy-bundle.schema.json",
    )


@pytest.fixture
def mvp_policy_bundle(real_policy_repository: FilesystemPolicyRepository) -> dict:
    return real_policy_repository.load_active_bundle()


@pytest.fixture
def in_memory_policy_repository(mvp_policy_bundle: dict) -> InMemoryPolicyRepository:
    return InMemoryPolicyRepository(mvp_policy_bundle)


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def audit_store() -> InMemoryAuditStore:
    return InMemoryAuditStore()


@pytest.fixture
def audit_chain(audit_store: InMemoryAuditStore, clock: FixedClock) -> AuditChain:
    return AuditChain(audit_store, DeterministicTestCanonicalizer(), clock)


@pytest.fixture
def approval_store() -> InMemoryApprovalStore:
    return InMemoryApprovalStore()


@pytest.fixture
def approval_service(approval_store: InMemoryApprovalStore, clock: FixedClock) -> ApprovalService:
    return ApprovalService(approval_store, clock)


@pytest.fixture
def capability_store() -> InMemoryCapabilityStore:
    return InMemoryCapabilityStore()


@pytest.fixture
def idempotency_store() -> InMemoryIdempotencyStore:
    return InMemoryIdempotencyStore()


@pytest.fixture
def budget_tracker() -> InMemoryBudgetTracker:
    return InMemoryBudgetTracker()


@pytest.fixture
def kill_switch() -> KillSwitch:
    return KillSwitch()


@pytest.fixture
def action_request_schema(schema) -> dict:
    return schema("action-request.schema.json")


def build_service(
    *,
    kernel_repository,
    policy_repository,
    action_request_schema: dict,
    clock: FixedClock,
    audit_chain: AuditChain,
    approval_service: ApprovalService,
    kill_switch: KillSwitch,
    idempotency_store: InMemoryIdempotencyStore,
    budget_tracker: InMemoryBudgetTracker,
    governance_available: bool = True,
    audit_available: bool = True,
) -> GovernanceService:
    return GovernanceService(
        kernel_repository=kernel_repository,
        policy_repository=policy_repository,
        action_request_schema=action_request_schema,
        clock=clock,
        audit_chain=audit_chain,
        approval_service=approval_service,
        kill_switch=kill_switch,
        idempotency_store=idempotency_store,
        budget_tracker=budget_tracker,
        config=GovernanceServiceConfig(
            governance_available=governance_available, audit_available=audit_available
        ),
    )


@pytest.fixture
def service_factory(
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
    def _make(**overrides):
        kwargs = dict(
            kernel_repository=real_kernel_repository,
            policy_repository=in_memory_policy_repository,
            action_request_schema=action_request_schema,
            clock=clock,
            audit_chain=audit_chain,
            approval_service=approval_service,
            kill_switch=kill_switch,
            idempotency_store=idempotency_store,
            budget_tracker=budget_tracker,
        )
        kwargs.update(overrides)
        return build_service(**kwargs)

    return _make


def make_action_request(
    *,
    verb: str,
    resource_type: str,
    resource_ref: str = "test-resource",
    environment: str = "staging",
    actor_id: str = "actor-1",
    actor_type: str = "orchestrator",
    idempotency_key: str | None = None,
    correlation_id: str | None = None,
    request_id: str | None = None,
) -> dict:
    return {
        "request_id": request_id or str(uuid.uuid4()),
        "idempotency_key": idempotency_key or str(uuid.uuid4()),
        "correlation_id": correlation_id or str(uuid.uuid4()),
        "actor": {
            "actor_id": actor_id,
            "actor_type": actor_type,
            "auth_method": "signed_capability",
        },
        "requested_at": "2026-01-01T00:00:00Z",
        "items": [
            {
                "item_id": "item-1",
                "verb": verb,
                "resource_type": resource_type,
                "resource_ref": resource_ref,
                "environment": environment,
            }
        ],
    }
