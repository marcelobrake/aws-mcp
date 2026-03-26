"""Additional guardrails for tools that can expose sensitive material."""
import hmac
import logging
import os

logger = logging.getLogger("aws_mcp")

SENSITIVE_ACCESS_TOKEN_ENV = "AWS_MCP_SENSITIVE_ACCESS_TOKEN"

SENSITIVE_ACCESS_PROPERTIES = {
    "sensitive_access_token": {
        "type": "string",
        "description": (
            "Out-of-band approval token configured in AWS_MCP_SENSITIVE_ACCESS_TOKEN. "
            "Required for operations that can return decrypted or secret values."
        ),
    },
    "sensitive_access_reason": {
        "type": "string",
        "description": (
            "Short human reason for retrieving sensitive data. Required for auditability."
        ),
    },
    "sensitive_access_acknowledged": {
        "type": "boolean",
        "description": (
            "Must be true to confirm that the response may contain secret or decrypted data."
        ),
    },
}


def require_sensitive_access(arguments: dict, tool_name: str) -> str | None:
    """Return an error string when extra authentication is missing or invalid."""
    configured_token = os.environ.get(SENSITIVE_ACCESS_TOKEN_ENV, "").strip()
    if not configured_token:
        return (
            "Sensitive access is disabled for this server instance. "
            f"Set {SENSITIVE_ACCESS_TOKEN_ENV} in the server environment to enable it."
        )

    provided_token = str(arguments.get("sensitive_access_token", "")).strip()
    if not provided_token:
        return "Sensitive access token is required for this operation."

    if arguments.get("sensitive_access_acknowledged") is not True:
        return "Set sensitive_access_acknowledged=true to confirm sensitive data access."

    reason = str(arguments.get("sensitive_access_reason", "")).strip()
    if len(reason) < 12:
        return "sensitive_access_reason must contain at least 12 characters."

    if not hmac.compare_digest(provided_token, configured_token):
        logger.warning(
            "Sensitive access denied due to invalid token",
            extra={"tool_name": tool_name},
        )
        return "Sensitive access token is invalid."

    logger.warning(
        "Sensitive access approved",
        extra={"tool_name": tool_name},
    )
    return None


def is_sensitive_execute_call(service: str, method: str, parameters: dict) -> bool:
    """Identify generic AWS calls that can return secret or decrypted material."""
    normalized_service = service.lower().replace("-", "_")
    normalized_method = method.lower().replace("-", "_")

    if normalized_service == "secretsmanager" and normalized_method in {
        "get_secret_value",
        "batch_get_secret_value",
    }:
        return True

    if normalized_service == "ssm" and normalized_method in {
        "get_parameter",
        "get_parameters",
        "get_parameters_by_path",
    }:
        return bool(parameters.get("WithDecryption", False))

    if normalized_service == "kms" and normalized_method in {
        "decrypt",
        "generate_data_key",
        "generate_data_key_pair",
    }:
        return True

    return False