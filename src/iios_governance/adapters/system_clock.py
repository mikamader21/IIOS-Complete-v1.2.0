from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Production clock. Never imported by tests — tests use an
    injectable fixed/stepping fake so no test depends on real time."""

    def now(self) -> datetime:
        return datetime.now(UTC)
