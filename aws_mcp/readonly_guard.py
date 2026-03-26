"""Readonly mode enforcement.

When the server runs with --readonly, mutating operations are either:
1. Executed with DryRun=True (if the AWS API supports it)
2. Blocked entirely with a clear error message

Read-only operations (list*, describe*, get*, etc.) always pass through.
"""
import logging
from dataclasses import dataclass

logger = logging.getLogger("aws_mcp")

# EC2 operations that accept a DryRun parameter
_EC2_DRY_RUN_OPS: set[str] = {
    "run_instances",
    "start_instances",
    "stop_instances",
    "terminate_instances",
    "reboot_instances",
    "create_security_group",
    "delete_security_group",
    "authorize_security_group_ingress",
    "authorize_security_group_egress",
    "revoke_security_group_ingress",
    "revoke_security_group_egress",
    "create_volume",
    "delete_volume",
    "attach_volume",
    "detach_volume",
    "create_snapshot",
    "delete_snapshot",
    "create_image",
    "deregister_image",
    "create_key_pair",
    "delete_key_pair",
    "allocate_address",
    "release_address",
    "associate_address",
    "disassociate_address",
    "create_tags",
    "delete_tags",
    "modify_instance_attribute",
    "create_launch_template",
    "create_vpc",
    "delete_vpc",
    "create_subnet",
    "delete_subnet",
}

# Map of service -> set of operations that support DryRun
DRY_RUN_OPERATIONS: dict[str, set[str]] = {
    "ec2": _EC2_DRY_RUN_OPS,
}

# Operation name prefixes that are inherently read-only
READ_ONLY_PREFIXES: tuple[str, ...] = (
    "describe",
    "list",
    "get",
    "head",
    "lookup",
    "check",
    "search",
    "query",
    "scan",
    "batch_get",
    "select",
)


def is_read_only_operation(operation: str) -> bool:
    """Return True if the operation name indicates a read-only call."""
    op = operation.lower().replace("-", "_")
    return any(op.startswith(prefix) for prefix in READ_ONLY_PREFIXES)


def supports_dry_run(service: str, operation: str) -> bool:
    """Return True if the (service, operation) pair supports DryRun."""
    svc = service.lower().replace("-", "_")
    op = operation.lower().replace("-", "_")
    return op in DRY_RUN_OPERATIONS.get(svc, set())


@dataclass(frozen=True)
class ReadonlyCheckResult:
    """Result of a readonly-mode check."""

    allowed: bool
    use_dry_run: bool
    error_message: str | None


def check_readonly(
    service: str, operation: str, readonly: bool
) -> ReadonlyCheckResult:
    """Evaluate whether an operation is permitted under the current mode.

    Args:
        service: AWS service name (e.g., "ec2", "s3").
        operation: API method name in snake_case (e.g., "stop_instances").
        readonly: Whether readonly mode is active.

    Returns:
        A ReadonlyCheckResult indicating if the call is allowed,
        whether to inject DryRun=True, and any error message.
    """
    if not readonly:
        return ReadonlyCheckResult(allowed=True, use_dry_run=False, error_message=None)

    if is_read_only_operation(operation):
        return ReadonlyCheckResult(allowed=True, use_dry_run=False, error_message=None)

    if supports_dry_run(service, operation):
        logger.info(
            f"Readonly mode: '{service}.{operation}' will execute with DryRun=True",
            extra={
                "tool_name": "readonly_guard",
                "aws_service": service,
                "aws_operation": operation,
                "dry_run": True,
            },
        )
        return ReadonlyCheckResult(allowed=True, use_dry_run=True, error_message=None)

    error_msg = (
        f"BLOCKED by readonly mode: '{service}.{operation}' is a mutating operation "
        f"and does not support DryRun. Remove --readonly to allow this operation."
    )
    logger.warning(
        error_msg,
        extra={
            "tool_name": "readonly_guard",
            "aws_service": service,
            "aws_operation": operation,
            "readonly": True,
        },
    )
    return ReadonlyCheckResult(allowed=False, use_dry_run=False, error_message=error_msg)
