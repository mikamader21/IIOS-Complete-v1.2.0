"""Test-oriented PolicyRepository: wraps an already-validated bundle held
in memory, so unit tests can exercise the Policy Engine without touching
the filesystem. Production wiring uses
adapters/filesystem/filesystem_policy_repository.py against the real,
checksum-verified governance/policy-bundles/ directory."""

from __future__ import annotations

from typing import Any


class InMemoryPolicyRepository:
    def __init__(self, bundle: dict[str, Any]) -> None:
        self._bundle = bundle

    def load_active_bundle(self) -> dict[str, Any]:
        return self._bundle
