# AGENTS.md

## Purpose

This repository exposes AWS data and control-plane actions to MCP clients. Treat every change as security-sensitive.

## Development Rules

1. Default to readonly behavior. Any new mutating capability must require explicit opt-in and document the blast radius.
2. Never return plaintext secrets, decrypted SecureString values, or KMS plaintext without going through aws_mcp/sensitive_guard.py.
3. When adding a new AWS escape hatch or a new tool that can reveal sensitive material, update both the tool schema and the generic aws_execute sensitive-operation map.
4. Do not log request payloads, approval tokens, secret identifiers with values, or decrypted content.
5. Keep telemetry opt-in only. Do not add fallback exporters that emit spans to stdout or stderr by default.

## Local Workflow

1. Run setup.sh in development clones so the repository installs hooks and local tooling.
2. Before pushing, the repository pre-push hook runs scripts/security_scan.sh.
3. If a scan tool is missing, install it instead of bypassing the hook.

## Sensitive Access Policy

1. Secrets Manager secret values require extra authentication.
2. SSM SecureString reads with decryption require extra authentication.
3. KMS operations that can reveal plaintext must use the same extra-auth path if added later.

## Expected Validation

1. Python syntax must stay valid.
2. Security hooks must remain executable.
3. README and example configuration must document any new security control.
