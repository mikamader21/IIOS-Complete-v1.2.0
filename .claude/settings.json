{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "defaultMode": "default",
    "disableBypassPermissionsMode": "disable",
    "allow": [
      "Bash(python scripts/verify_foundation.py)",
      "Bash(python scripts/verify_invariant_kernel.py)",
      "Bash(git status)",
      "Bash(git diff *)"
    ],
    "ask": [
      "Edit",
      "Write",
      "Bash(git add *)",
      "Bash(git commit *)"
    ],
    "deny": [
      "mcp__*",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(./**/*.pem)",
      "Read(./**/*.key)",
      "Bash(curl *)",
      "Bash(wget *)",
      "Bash(ssh *)",
      "Bash(scp *)",
      "Bash(rsync *)",
      "Bash(kubectl *)",
      "Bash(terraform apply *)",
      "Bash(docker push *)",
      "Bash(git push --force *)"
    ]
  },
  "disableClaudeAiConnectors": true,
  "disableAutoMode": "disable",
  "disableRemoteControl": true,
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/pretool_guard.py\""
          }
        ]
      }
    ]
  }
}
