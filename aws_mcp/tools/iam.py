"""IAM tools: users, roles, and policies."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_iam_list_users",
    description="List IAM users in the AWS account with optional path prefix filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "path_prefix": {
                "type": "string",
                "description": "IAM path prefix filter (default: '/')",
            },
            "max_items": {
                "type": "integer",
                "description": "Maximum number of users to return",
            },
        },
    },
    is_read_only=True,
)
async def list_users(arguments: dict) -> str:
    def _execute():
        client = get_client("iam", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "path_prefix" in arguments:
            kwargs["PathPrefix"] = arguments["path_prefix"]
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_users(**kwargs)
        users = response.get("Users", [])
        return users

    users = await asyncio.to_thread(_execute)
    return json.dumps({"users": users, "count": len(users)}, default=str)


@tool(
    name="aws_iam_list_roles",
    description="List IAM roles in the AWS account with optional path prefix filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "path_prefix": {
                "type": "string",
                "description": "IAM path prefix filter (default: '/')",
            },
            "max_items": {
                "type": "integer",
                "description": "Maximum number of roles to return",
            },
        },
    },
    is_read_only=True,
)
async def list_roles(arguments: dict) -> str:
    def _execute():
        client = get_client("iam", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "path_prefix" in arguments:
            kwargs["PathPrefix"] = arguments["path_prefix"]
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_roles(**kwargs)
        roles = response.get("Roles", [])
        return roles

    roles = await asyncio.to_thread(_execute)
    return json.dumps({"roles": roles, "count": len(roles)}, default=str)


@tool(
    name="aws_iam_list_policies",
    description=(
        "List IAM policies. By default lists only customer-managed policies. "
        "Set scope to 'AWS' for AWS-managed or 'All' for both."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "scope": {
                "type": "string",
                "enum": ["All", "AWS", "Local"],
                "description": "Policy scope: 'All', 'AWS' (managed), or 'Local' (customer). Default: 'Local'",
            },
            "max_items": {
                "type": "integer",
                "description": "Maximum number of policies to return",
            },
        },
    },
    is_read_only=True,
)
async def list_policies(arguments: dict) -> str:
    def _execute():
        client = get_client("iam", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"Scope": arguments.get("scope", "Local")}
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_policies(**kwargs)
        policies = response.get("Policies", [])
        return policies

    policies = await asyncio.to_thread(_execute)
    return json.dumps({"policies": policies, "count": len(policies)}, default=str)
