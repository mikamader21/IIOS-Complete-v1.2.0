"""Injectable clock — no domain logic reads the real wall clock directly,
so tests are never dependent on real time (required test property)."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime:
        """Return the current instant, timezone-aware, UTC."""
        ...
