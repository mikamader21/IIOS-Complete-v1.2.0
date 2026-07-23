from __future__ import annotations

from iios_governance.adapters.memory.in_memory_audit_store import InMemoryAuditStore
from iios_governance.domain.audit_chain import AuditChain
from iios_governance.domain.models import GENESIS_HASH
from tests.governance.fakes import DeterministicTestCanonicalizer, FixedClock


def _chain() -> tuple[AuditChain, InMemoryAuditStore]:
    store = InMemoryAuditStore()
    return AuditChain(store, DeterministicTestCanonicalizer(), FixedClock()), store


def test_genesis_event_has_sentinel_previous_hash() -> None:
    chain, store = _chain()
    event = chain.append(
        partition="c1", event_type="request_received", actor="a1", correlation_id="c1"
    )
    assert event.previous_event_hash == GENESIS_HASH
    assert len(event.event_hash) == 64


def test_chain_links_events() -> None:
    chain, store = _chain()
    e1 = chain.append(
        partition="c1", event_type="request_received", actor="a1", correlation_id="c1"
    )
    e2 = chain.append(
        partition="c1",
        event_type="policy_decision",
        actor="a1",
        correlation_id="c1",
        decision="allow",
    )
    assert e2.previous_event_hash == e1.event_hash


def test_verify_chain_passes_for_untampered_chain() -> None:
    chain, store = _chain()
    chain.append(partition="c1", event_type="request_received", actor="a1", correlation_id="c1")
    chain.append(
        partition="c1",
        event_type="policy_decision",
        actor="a1",
        correlation_id="c1",
        decision="allow",
    )
    ok, break_index = chain.verify_chain(partition="c1")
    assert ok is True
    assert break_index is None


def test_tampering_is_detected() -> None:
    chain, store = _chain()
    chain.append(partition="c1", event_type="request_received", actor="a1", correlation_id="c1")
    chain.append(
        partition="c1",
        event_type="policy_decision",
        actor="a1",
        correlation_id="c1",
        decision="allow",
    )

    events = store.iter_chain(partition="c1")
    # Mutate a field post-hoc without recomputing the hash — simulates
    # unauthorized modification of stored audit data.
    tampered = events[0]
    object.__setattr__(tampered, "actor", "attacker")

    ok, break_index = chain.verify_chain(partition="c1")
    assert ok is False
    assert break_index == 0


def test_reordering_events_breaks_the_chain() -> None:
    chain, store = _chain()
    chain.append(partition="c1", event_type="request_received", actor="a1", correlation_id="c1")
    chain.append(
        partition="c1",
        event_type="policy_decision",
        actor="a1",
        correlation_id="c1",
        decision="allow",
    )

    events = store._events["c1"]  # test-internal access to reorder
    events[0], events[1] = events[1], events[0]

    ok, break_index = chain.verify_chain(partition="c1")
    assert ok is False


def test_separate_partitions_do_not_cross_link() -> None:
    chain, store = _chain()
    e1 = chain.append(
        partition="c1", event_type="request_received", actor="a1", correlation_id="c1"
    )
    e2 = chain.append(
        partition="c2", event_type="request_received", actor="a2", correlation_id="c2"
    )
    assert e1.previous_event_hash == GENESIS_HASH
    assert e2.previous_event_hash == GENESIS_HASH
