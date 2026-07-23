"""The production clock is exercised once here for coverage/shape only —
no test asserts on a specific real-time value (that would violate the
'no test depends on real time' requirement)."""

from __future__ import annotations

from datetime import UTC

from iios_governance.adapters.system_clock import SystemClock


def test_system_clock_returns_timezone_aware_utc() -> None:
    clock = SystemClock()
    now = clock.now()
    assert now.tzinfo is not None
    assert now.utcoffset() == UTC.utcoffset(None)
