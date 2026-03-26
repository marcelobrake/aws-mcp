"""General-purpose AWS API execution tool.

Provides a flexible escape hatch for any AWS service call not covered
by the specific tool modules. Respects readonly mode via the readonly guard.
"""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from ..readonly_guard import check_readonly
from ..sensitive_guard import (
    SENSITIVE_ACCESS_PROPERTIES,
    is_sensitive_execute_call,
    require_sensitive_access,
)
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_execute",
    description=(
        "Execute any AWS API call by specifying service, method, and parameters. "
        "Use this for AWS operations not covered by other tools. "
        "In --readonly mode: read-only operations pass through, mutating operations "
        "with DryRun support run as dry-run, and all other mutations are blocked."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            **SENSITIVE_ACCESS_PROPERTIES,
            "service": {
                "type": "string",
                "description": (
                    "AWS service name as used by boto3 "
                    "(e.g., 'ec2', 's3', 'lambda', 'ecs', 'rds', 'dynamodb', 'sqs', 'sns')"
                ),
            },
            "method": {
                "type": "string",
                "description": (
                    "API method name in snake_case "
                    "(e.g., 'describe_instances', 'list_buckets', 'get_function')"
                ),
            },
            "parameters": {
                "type": "object",
                "description": (
                    "Method parameters as key-value pairs matching the boto3 API "
                    "(e.g., {\"InstanceIds\": [\"i-1234\"], \"DryRun\": false})"
                ),
            },
        },
        "required": ["service", "method"],
    },
    is_read_only=False,
)
async def execute(arguments: dict) -> str:
    config = get_config()
    service = arguments["service"]
    method = arguments["method"]
    params = dict(arguments.get("parameters", {}))

    if is_sensitive_execute_call(service, method, params):
        sensitive_error = require_sensitive_access(arguments, "aws_execute")
        if sensitive_error:
            return json.dumps({"error": sensitive_error, "sensitive": True})

    # Readonly guard
    result = check_readonly(service, method, config.readonly)
    if not result.allowed:
        return json.dumps({"error": result.error_message, "readonly": True})
    if result.use_dry_run:
        params["DryRun"] = True

    def _execute():
        client = get_client(service, arguments.get("profile"), arguments.get("region"))
        api_method = getattr(client, method, None)
        if api_method is None:
            return {
                "error": f"Method '{method}' not found on service '{service}'. "
                f"Check the boto3 documentation for valid method names."
            }

        try:
            response = api_method(**params)
            # Clean up metadata for readability
            if isinstance(response, dict):
                response.pop("ResponseMetadata", None)
            return response
        except client.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            # DryRunOperation means the call would have succeeded
            if error_code == "DryRunOperation":
                return {
                    "dry_run": True,
                    "message": f"DryRun succeeded: '{service}.{method}' would be allowed",
                    "parameters": params,
                }
            raise

    try:
        response = await asyncio.to_thread(_execute)
    except Exception as e:
        logger.error(
            f"aws_execute failed: {service}.{method}: {e}",
            extra={
                "tool_name": "aws_execute",
                "aws_service": service,
                "aws_operation": method,
            },
            exc_info=True,
        )
        return json.dumps({"error": str(e)}, default=str)

    return json.dumps(response, default=str)
