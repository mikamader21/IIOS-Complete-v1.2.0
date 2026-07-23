"""Loads the REAL, ratified Invariant Kernel from governance/invariant-kernel/.

Never writes to that directory. Fails closed on any mismatch, exactly
like scripts/verify_invariant_kernel.py — this adapter does not
reimplement kernel semantics, it reuses the same checksum algorithm
against the same files.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from iios_governance.adapters.filesystem.checksum import canonical_sha256
from iios_governance.domain.errors import KernelChecksumMismatchError, KernelUnavailableError


class FilesystemKernelRepository:
    def __init__(self, kernel_dir: Path) -> None:
        self._invariants_path = kernel_dir / "invariants.json"
        self._manifest_path = kernel_dir / "manifest.json"

    def load_verified_kernel(self) -> tuple[dict[str, Any], str]:
        if not self._invariants_path.exists() or not self._manifest_path.exists():
            raise KernelUnavailableError(
                f"missing Kernel file(s) under {self._invariants_path.parent}"
            )
        try:
            invariants = json.loads(self._invariants_path.read_text(encoding="utf-8"))
            manifest = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - fail closed regardless of cause
            raise KernelUnavailableError(f"cannot parse Kernel: {exc}") from exc

        actual = canonical_sha256(self._invariants_path)
        expected = manifest.get("sha256")
        if actual != expected:
            raise KernelChecksumMismatchError(
                f"Kernel checksum mismatch: expected {expected}, got {actual}"
            )
        if invariants.get("default_decision") != "deny" or invariants.get("fail_mode") != "closed":
            raise KernelUnavailableError("Kernel does not declare deny/closed defaults")

        return invariants, actual
