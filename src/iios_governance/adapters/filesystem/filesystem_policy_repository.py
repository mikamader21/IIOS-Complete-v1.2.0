"""Loads a policy bundle from disk (governance/policy-bundles/<name>/),
checksum-verified the same way as the Invariant Kernel, then validated
against governance/schemas/policy-bundle.schema.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema.validators import Draft202012Validator

from iios_governance.adapters.filesystem.checksum import canonical_sha256
from iios_governance.domain.errors import (
    PolicyBundleChecksumMismatchError,
    PolicyBundleInvalidError,
    PolicyBundleUnavailableError,
)


class FilesystemPolicyRepository:
    def __init__(self, bundle_dir: Path, schema_path: Path) -> None:
        self._policy_path = bundle_dir / "policy.json"
        self._manifest_path = bundle_dir / "manifest.json"
        self._schema_path = schema_path

    def load_active_bundle(self) -> dict[str, Any]:
        if not self._policy_path.exists() or not self._manifest_path.exists():
            raise PolicyBundleUnavailableError(
                f"missing policy bundle file(s) under {self._policy_path.parent}"
            )
        try:
            bundle = json.loads(self._policy_path.read_text(encoding="utf-8"))
            manifest = json.loads(self._manifest_path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - fail closed regardless of cause
            raise PolicyBundleUnavailableError(f"cannot parse policy bundle: {exc}") from exc

        actual = canonical_sha256(self._policy_path)
        expected = manifest.get("sha256")
        if actual != expected:
            raise PolicyBundleChecksumMismatchError(
                f"policy bundle checksum mismatch: expected {expected}, got {actual}"
            )

        schema = json.loads(self._schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(bundle), key=lambda e: e.path)
        if errors:
            raise PolicyBundleInvalidError(
                "policy bundle fails schema validation: "
                + "; ".join(f"{list(e.path)}: {e.message}" for e in errors)
            )
        if bundle.get("default_decision") != "deny":
            raise PolicyBundleInvalidError("policy bundle default_decision must be deny")

        limits = bundle.get("limits") or {}
        max_rules = limits.get("max_rules", 200)
        if len(bundle["rules"]) > max_rules:
            raise PolicyBundleInvalidError(
                f"policy bundle has {len(bundle['rules'])} rules, exceeding max_rules={max_rules}"
            )

        return bundle
