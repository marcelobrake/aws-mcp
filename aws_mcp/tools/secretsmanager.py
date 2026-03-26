"""Secrets Manager tools: list, describe, and retrieve secrets."""
import asyncio
import json

from ..aws_client import get_client
from ..sensitive_guard import SENSITIVE_ACCESS_PROPERTIES, require_sensitive_access
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_secretsmanager_list_secrets",
    description="List secrets in AWS Secrets Manager (names and metadata, not values).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum secrets to return",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Key": {
                            "type": "string",
                            "enum": ["description", "name", "tag-key", "tag-value", "all"],
                        },
                        "Values": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "description": "Filters (e.g., [{\"Key\": \"name\", \"Values\": [\"prod\"]}])",
            },
        },
    },
    is_read_only=True,
)
async def list_secrets(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "secretsmanager", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]

        response = client.list_secrets(**kwargs)
        secrets = [
            {
                "Name": s.get("Name"),
                "ARN": s.get("ARN"),
                "Description": s.get("Description"),
                "LastChangedDate": s.get("LastChangedDate"),
                "Tags": s.get("Tags"),
            }
            for s in response.get("SecretList", [])
        ]
        return secrets

    secrets = await asyncio.to_thread(_execute)
    return json.dumps({"secrets": secrets, "count": len(secrets)}, default=str)


@tool(
    name="aws_secretsmanager_describe_secret",
    description="Get metadata about a secret (rotation, replication, tags) without retrieving the value.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            **SENSITIVE_ACCESS_PROPERTIES,
            "secret_id": {
                "type": "string",
                "description": "Secret name or ARN",
            },
        },
        "required": ["secret_id"],
    },
    is_read_only=True,
)
async def describe_secret(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "secretsmanager", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_secret(SecretId=arguments["secret_id"])
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_secretsmanager_get_secret_value",
    description=(
        "Retrieve the actual secret value. Use with caution — the value "
        "will appear in the conversation. Blocked in --readonly mode."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "secret_id": {
                "type": "string",
                "description": "Secret name or ARN",
            },
            "version_id": {
                "type": "string",
                "description": "Specific version ID (optional)",
            },
            "version_stage": {
                "type": "string",
                "description": "Version stage (default: AWSCURRENT)",
            },
        },
        "required": ["secret_id"],
    },
    is_read_only=False,
)
async def get_secret_value(arguments: dict) -> str:
    from ..config import get_config

    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: GetSecretValue is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    sensitive_error = require_sensitive_access(
        arguments, "aws_secretsmanager_get_secret_value"
    )
    if sensitive_error:
        return json.dumps({"error": sensitive_error, "sensitive": True})

    def _execute():
        client = get_client(
            "secretsmanager", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"SecretId": arguments["secret_id"]}
        if "version_id" in arguments:
            kwargs["VersionId"] = arguments["version_id"]
        if "version_stage" in arguments:
            kwargs["VersionStage"] = arguments["version_stage"]

        response = client.get_secret_value(**kwargs)
        return {
            "Name": response.get("Name"),
            "SecretString": response.get("SecretString"),
            "VersionId": response.get("VersionId"),
            "VersionStages": response.get("VersionStages"),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
