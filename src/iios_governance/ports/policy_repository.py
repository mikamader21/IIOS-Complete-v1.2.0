from __future__ import annotations

from typing import Any, Protocol


class PolicyRepository(Protocol):
    def load_active_bundle(self) -> dict[str, Any]:
        """Return the active policy bundle as a validated dict, or raise
        PolicyBundleUnavailableError / PolicyBundleChecksumMismatchError /
        PolicyBundleInvalidError. Never returns a partially-valid bundle."""
        ...
