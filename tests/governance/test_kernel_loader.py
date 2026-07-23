from __future__ import annotations

import json
from pathlib import Path

import pytest

from iios_governance.adapters.filesystem.filesystem_kernel_repository import (
    FilesystemKernelRepository,
)
from iios_governance.domain.errors import KernelChecksumMismatchError, KernelUnavailableError


def test_real_kernel_loads_and_verifies(real_kernel_repository: FilesystemKernelRepository) -> None:
    invariants, checksum = real_kernel_repository.load_verified_kernel()
    assert invariants["default_decision"] == "deny"
    assert invariants["fail_mode"] == "closed"
    assert len(checksum) == 64
    assert isinstance(invariants["invariants"], list) and invariants["invariants"]


def test_missing_kernel_fails_closed(tmp_path: Path) -> None:
    repo = FilesystemKernelRepository(tmp_path / "does-not-exist")
    with pytest.raises(KernelUnavailableError):
        repo.load_verified_kernel()


def test_tampered_kernel_fails_closed(
    tmp_path: Path, real_kernel_repository: FilesystemKernelRepository
) -> None:
    real_invariants, real_checksum = real_kernel_repository.load_verified_kernel()

    kernel_dir = tmp_path / "kernel"
    kernel_dir.mkdir()
    tampered = dict(real_invariants)
    tampered["default_decision"] = "deny"  # keep required const valid
    tampered["invariants"] = [
        *real_invariants["invariants"],
        {"id": "INV-999", "statement": "tampered", "enforcement": "n/a"},
    ]
    (kernel_dir / "invariants.json").write_text(json.dumps(tampered), encoding="utf-8")
    (kernel_dir / "manifest.json").write_text(
        json.dumps({"sha256": real_checksum}), encoding="utf-8"
    )  # stale checksum, doesn't match tampered content

    repo = FilesystemKernelRepository(kernel_dir)
    with pytest.raises(KernelChecksumMismatchError):
        repo.load_verified_kernel()


def test_kernel_missing_manifest_fails_closed(
    tmp_path: Path, real_kernel_repository: FilesystemKernelRepository
) -> None:
    invariants, _ = real_kernel_repository.load_verified_kernel()
    kernel_dir = tmp_path / "kernel-no-manifest"
    kernel_dir.mkdir()
    (kernel_dir / "invariants.json").write_text(json.dumps(invariants), encoding="utf-8")
    repo = FilesystemKernelRepository(kernel_dir)
    with pytest.raises(KernelUnavailableError):
        repo.load_verified_kernel()


def test_kernel_malformed_json_fails_closed(tmp_path: Path) -> None:
    kernel_dir = tmp_path / "kernel-malformed"
    kernel_dir.mkdir()
    (kernel_dir / "invariants.json").write_text("{not valid json", encoding="utf-8")
    (kernel_dir / "manifest.json").write_text('{"sha256": "x"}', encoding="utf-8")
    repo = FilesystemKernelRepository(kernel_dir)
    with pytest.raises(KernelUnavailableError):
        repo.load_verified_kernel()


def test_kernel_wrong_defaults_rejected(
    tmp_path: Path, real_kernel_repository: FilesystemKernelRepository
) -> None:
    from iios_governance.adapters.filesystem.checksum import canonical_sha256

    invariants, _ = real_kernel_repository.load_verified_kernel()
    kernel_dir = tmp_path / "kernel-wrong-defaults"
    kernel_dir.mkdir()
    bad = {**invariants, "fail_mode": "open"}  # never valid — deny/closed only
    (kernel_dir / "invariants.json").write_text(json.dumps(bad), encoding="utf-8")
    checksum = canonical_sha256(kernel_dir / "invariants.json")
    (kernel_dir / "manifest.json").write_text(json.dumps({"sha256": checksum}), encoding="utf-8")
    repo = FilesystemKernelRepository(kernel_dir)
    with pytest.raises(KernelUnavailableError):
        repo.load_verified_kernel()
