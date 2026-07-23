"""Domain errors. All are fail-closed signals, never silent fallbacks."""

from __future__ import annotations


class GovernanceError(Exception):
    """Base for every deliberate, typed failure in this package."""


class KernelUnavailableError(GovernanceError):
    """Invariant Kernel missing, unreadable, or malformed."""


class KernelChecksumMismatchError(GovernanceError):
    """governance/invariant-kernel/invariants.json does not match manifest.json."""


class PolicyBundleUnavailableError(GovernanceError):
    """Policy bundle missing, unreadable, or malformed."""


class PolicyBundleChecksumMismatchError(GovernanceError):
    """Policy bundle content does not match its manifest checksum."""


class PolicyBundleInvalidError(GovernanceError):
    """Policy bundle fails structural or mandatory-condition checks."""


class SchemaValidationError(GovernanceError):
    """An instance failed validation against its JSON Schema."""

    def __init__(self, message: str, schema_errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.schema_errors = schema_errors or []


class SelfApprovalError(GovernanceError):
    """approver_id == requested_by."""


class CapabilityError(GovernanceError):
    """Base for capability issuance/consumption failures."""


class CryptoNotImplementedError(GovernanceError):
    """Production signing/verification is intentionally not implemented here."""
