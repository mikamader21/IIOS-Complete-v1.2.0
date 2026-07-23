from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
required = [
    "AGENTS.md", "CLAUDE.md", "PROJECT_STATE.md",
    "docs/00_MASTER_CHARTER.md", "docs/01_CONSTITUTION.md",
    "docs/02_SYSTEM_ARCHITECTURE.md", "docs/03_GOVERNANCE_SECURITY.md",
    "docs/18_AUDIT_DISPOSITION.md", "docs/20_OWNER_RATIFICATION.md",
    "config/model-registry.json", ".claude/settings.json",
    ".github/workflows/verify-foundation.yml",
    "governance/invariant-kernel/invariants.json",
    "governance/invariant-kernel/manifest.json",
    ".gitattributes",
    "docs/21_GOVERNANCE_CORE_SPEC.md",
    "docs/22_POLICY_ENGINE_EVALUATION.md",
    "docs/23_CAPABILITY_MODEL.md",
    "docs/24_APPROVAL_MODEL.md",
    "docs/25_AUDIT_EVENT_MODEL.md",
    "docs/26_KILL_SWITCH_SPEC.md",
    "docs/ADR/ADR-0010-GOVERNANCE-CORE-BOUNDARIES.md",
    "governance/schemas/action-request.schema.json",
    "governance/schemas/policy-decision.schema.json",
    "governance/schemas/approval.schema.json",
    "governance/schemas/capability-claims.schema.json",
    "governance/schemas/capability-protected-header.schema.json",
    "governance/schemas/capability-token.schema.json",
    "governance/schemas/audit-event.schema.json",
    "governance/schemas/kill-switch-event.schema.json",
    "docs/ADR/ADR-0011-GOVERNANCE-MVP-OWNER-DECISIONS.md",
    "OWNER_PROFILE.md",
    "AUTONOMY_PROTOCOL.md",
    "MASTER_IMPLEMENTATION_PROGRAM.md",
    "BACKLOG.md",
    "docs/DOMAIN_CATALOG.md",
    "docs/BRAIN_REGISTRY.md",
    "docs/AGENT_REGISTRY.md",
    "docs/SKILL_CATALOG.md",
    "docs/WORKFLOW_REGISTRY.md",
    "docs/TOOL_REGISTRY.md",
    "docs/MODEL_ROUTING.md",
    "docs/MEMORY_ARCHITECTURE.md",
    "docs/SELF_EVOLUTION_PROTOCOL.md",
    "docs/HANDOFF_PROTOCOL.md",
    "docs/AUTONOMY_ACCEPTANCE_TESTS.md",
    "work/NOW.md",
    "work/NEXT.md",
    "work/BLOCKED.md",
    "work/DONE.md",
    "docs/30_GOVERNANCE_IMPLEMENTATION_SKELETON.md",
    "docs/ADR/ADR-0012-POLICY-BUNDLE-FORMAT.md",
    "pyproject.toml",
    "governance/schemas/policy-bundle.schema.json",
    "governance/policy-bundles/mvp/policy.json",
    "governance/policy-bundles/mvp/manifest.json",
    "src/iios_governance/__init__.py",
    "src/iios_governance/domain/models.py",
    "src/iios_governance/domain/action_classifier.py",
    "src/iios_governance/domain/policy_engine.py",
    "src/iios_governance/domain/approval_service.py",
    "src/iios_governance/domain/capability_service.py",
    "src/iios_governance/domain/audit_chain.py",
    "src/iios_governance/domain/kill_switch.py",
    "src/iios_governance/application/governance_service.py",
    "tests/governance/conftest.py",
    "docs/31_HERMES_DEPLOYMENT_PACKAGE.md",
    "docs/ADR/ADR-0013-HERMES-VPS-DEPLOYMENT-MODEL.md",
    "deploy/hermes/README.md",
    "deploy/hermes/directory-layout.md",
    "deploy/hermes/scripts/create-service-user.sh",
    "deploy/hermes/scripts/bootstrap-directories.sh",
    "deploy/hermes/scripts/run-backup.sh",
    "deploy/hermes/scripts/run-healthcheck.sh",
    "deploy/hermes/systemd/hermes-backup.service",
    "deploy/hermes/systemd/hermes-backup.timer",
    "deploy/hermes/systemd/hermes-healthcheck.service",
    "deploy/hermes/systemd/hermes-healthcheck.timer",
    "deploy/hermes/firewall/apply-ufw-rules.sh",
    "deploy/hermes/firewall/egress-allowlist.md",
    "deploy/hermes/secrets/env.template",
    "deploy/hermes/secrets/README.md",
    "deploy/hermes/core/docker-compose.yml.template",
    "deploy/hermes/core/compose.env.example",
    "deploy/hermes/profiles/ict-trading.profile.json",
    "deploy/hermes/profiles/ict-trading.config.yaml.template",
    "deploy/hermes/runbooks/INSTALL.md",
    "deploy/hermes/runbooks/UNINSTALL_ROLLBACK.md",
    "deploy/hermes/runbooks/UPDATE_ROLLBACK.md",
    "deploy/hermes/runbooks/BACKUP_RESTORE.md",
    "deploy/hermes/runbooks/HEALTH_CHECKS.md",
    "docs/32_ONYX_EXECUTIVE_ORCHESTRATOR_SPEC.md",
    "deploy/hermes/profiles/onyx/onyx.profile.json",
]
errors = []
for rel in required:
    if not (root / rel).exists():
        errors.append(f"missing: {rel}")

gitattributes = (root / ".gitattributes").read_text(encoding="utf-8") if (root / ".gitattributes").exists() else ""
if not re.search(r"^governance/invariant-kernel/\*\.json\s+text\s+eol=lf\s*$", gitattributes, flags=re.M):
    errors.append(".gitattributes missing explicit eol=lf rule for governance/invariant-kernel/*.json")

if (root / ".hermes.md").exists() or (root / "HERMES.md").exists():
    errors.append("root Hermes context overrides AGENTS.md")

claude = (root / "CLAUDE.md").read_text(encoding="utf-8") if (root / "CLAUDE.md").exists() else ""
if "@AGENTS.md" not in claude:
    errors.append("CLAUDE.md does not import AGENTS.md")

agents = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").exists() else ""
if len(agents) > 20000:
    errors.append("AGENTS.md exceeds 20,000 characters")

# Structural schema validation only: valid JSON and (for governance/schemas/*)
# a declared Draft 2020-12 $schema. This is NOT full JSON Schema Draft 2020-12
# conformance validation, NOT meta-schema validation, and does NOT check that
# any real instance validates against these schemas. See
# governance/schemas/README.md "Validation scope: what 'verified' means today"
# for the full statement and the future implementation requirement (pinned
# Draft 2020-12 validation library, meta-schema validation, positive/negative
# tests per schema — none added in this change).
json_required = [
    "config/model-registry.json", ".claude/settings.json",
    "governance/schemas/action-request.schema.json",
    "governance/schemas/policy-decision.schema.json",
    "governance/schemas/approval.schema.json",
    "governance/schemas/capability-claims.schema.json",
    "governance/schemas/capability-protected-header.schema.json",
    "governance/schemas/capability-token.schema.json",
    "governance/schemas/audit-event.schema.json",
    "governance/schemas/kill-switch-event.schema.json",
    "governance/schemas/policy-bundle.schema.json",
    "governance/policy-bundles/mvp/policy.json",
    "governance/policy-bundles/mvp/manifest.json",
    "deploy/hermes/profiles/ict-trading.profile.json",
    "deploy/hermes/profiles/onyx/onyx.profile.json",
]
schema_files = {f for f in json_required if f.startswith("governance/schemas/")}
onyx_manifest_path = "deploy/hermes/profiles/onyx/onyx.profile.json"
for rel in json_required:
    try:
        parsed = json.loads((root / rel).read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON in {rel}: {exc}")
        continue
    if rel in schema_files and parsed.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        errors.append(f"{rel} does not declare Draft 2020-12 $schema")
    if rel == onyx_manifest_path:
        # ONYX v0.1 ("Executive Observer") must stay structurally read-only and
        # not-activated — this is not just documentation prose, it is
        # mechanically checked so a future edit cannot silently loosen it.
        expected_scalars = {
            "status": "specified",
            "activation_state": "not_activated",
            "execution_mode": "read_only",
        }
        for field, expected in expected_scalars.items():
            if parsed.get(field) != expected:
                errors.append(f"{rel}: {field} must be {expected!r}, got {parsed.get(field)!r}")
        for field in ("capabilities", "tools", "secrets"):
            if parsed.get(field) != []:
                errors.append(f"{rel}: {field} must be an empty list, got {parsed.get(field)!r}")
        for flag in (
            "financial_execution", "self_approval", "main_merge",
            "release_creation", "vps_modification",
        ):
            if parsed.get(flag) is not False:
                errors.append(f"{rel}: {flag} must be false, got {parsed.get(flag)!r}")
        terminal = parsed.get("terminal", {})
        if terminal.get("backend") != "local":
            errors.append(f"{rel}: terminal.backend must be 'local', got {terminal.get('backend')!r}")
        if terminal.get("home_mode") != "profile":
            errors.append(f"{rel}: terminal.home_mode must be 'profile', got {terminal.get('home_mode')!r}")
        if terminal.get("docker_forward_env") != []:
            errors.append(
                f"{rel}: terminal.docker_forward_env must be an empty list, "
                f"got {terminal.get('docker_forward_env')!r}"
            )

_SKIP_DIR_NAMES = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", "node_modules", ".next", "dist", "build",
}


def _is_skipped(path: Path) -> bool:
    return any(part in _SKIP_DIR_NAMES or part.endswith(".egg-info") for part in path.parts)


for path in root.rglob("*"):
    if (
        path.resolve() == Path(__file__).resolve()
        or not path.is_file()
        or path.stat().st_size >= 2_000_000
        or _is_skipped(path)
    ):
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        continue
    if re.search(r"(?i)(sk-ant-|sk-or-|api[_-]?key\s*=\s*[^<\s])", text):
        errors.append(f"possible secret in {path.relative_to(root)}")

kernel_check = subprocess.run(
    [sys.executable, str(root / "scripts" / "verify_invariant_kernel.py")],
    capture_output=True, text=True
)
if kernel_check.returncode != 0:
    errors.append(kernel_check.stdout.strip() or kernel_check.stderr.strip() or "Invariant Kernel check failed")

if errors:
    print("\n".join("ERROR: " + error for error in errors))
    sys.exit(1)
print("Foundation verification passed")
