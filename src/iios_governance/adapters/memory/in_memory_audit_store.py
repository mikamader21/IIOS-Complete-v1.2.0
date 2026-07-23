from __future__ import annotations

from collections import defaultdict

from iios_governance.domain.models import GENESIS_HASH, AuditEvent


class InMemoryAuditStore:
    def __init__(self) -> None:
        self._events: dict[str, list[AuditEvent]] = defaultdict(list)

    def append(self, event: AuditEvent) -> None:
        self._events[self._partition_of(event)].append(event)

    @staticmethod
    def _partition_of(event: AuditEvent) -> str:
        # Partitioned by correlation_id per docs/25_AUDIT_EVENT_MODEL.md
        # "Chains are scoped per correlation_id for readability."
        return event.correlation_id

    def last_event_hash(self, *, partition: str) -> str:
        events = self._events.get(partition, [])
        return events[-1].event_hash if events else GENESIS_HASH

    def iter_chain(self, *, partition: str) -> list[AuditEvent]:
        return list(self._events.get(partition, []))

    def all_events(self) -> list[AuditEvent]:
        return [e for events in self._events.values() for e in events]
