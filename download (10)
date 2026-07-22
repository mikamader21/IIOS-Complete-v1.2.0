from pathlib import Path
import hashlib
import json
import sys

root = Path(__file__).resolve().parents[1]
kernel = root / "governance" / "invariant-kernel"
policy_path = kernel / "invariants.json"
manifest_path = kernel / "manifest.json"

errors = []
try:
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
except Exception as exc:
    print(f"ERROR: cannot load Invariant Kernel: {exc}")
    sys.exit(1)

required = {"schema_version", "policy_version", "default_decision", "fail_mode", "invariants"}
missing = required - set(policy)
if missing:
    errors.append(f"policy missing fields: {sorted(missing)}")
if policy.get("default_decision") != "deny":
    errors.append("default_decision must be deny")
if policy.get("fail_mode") != "closed":
    errors.append("fail_mode must be closed")
if not isinstance(policy.get("invariants"), list) or not policy.get("invariants"):
    errors.append("invariants must be a non-empty list")
else:
    ids = []
    for item in policy["invariants"]:
        if not isinstance(item, dict) or not {"id", "statement", "enforcement"} <= set(item):
            errors.append("each invariant requires id, statement and enforcement")
            continue
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        errors.append("invariant IDs must be unique")

actual = hashlib.sha256(policy_path.read_bytes()).hexdigest()
expected = manifest.get("sha256")
if actual != expected:
    errors.append(f"checksum mismatch: expected {expected}, got {actual}")

if errors:
    for error in errors:
        print(f"ERROR: {error}")
    sys.exit(1)
print("Invariant Kernel verification passed")
