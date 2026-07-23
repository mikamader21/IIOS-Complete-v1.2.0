from __future__ import annotations

from typing import Any, Protocol


class KernelRepository(Protocol):
    def load_verified_kernel(self) -> tuple[dict[str, Any], str]:
        """Return (invariants_dict, canonical_sha256_checksum), or raise
        KernelUnavailableError / KernelChecksumMismatchError. Never
        returns a Kernel whose checksum does not match its manifest."""
        ...
