"""Cognito tools: user pools, users, and groups."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_cognito_list_user_pools",
    description="List Cognito user pools in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum pools to return (default: 60)",
            },
        },
    },
    is_read_only=True,
)
async def list_user_pools(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cognito-idp", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_user_pools(
            MaxResults=arguments.get("max_results", 60)
        )
        return response.get("UserPools", [])

    pools = await asyncio.to_thread(_execute)
    return json.dumps({"user_pools": pools, "count": len(pools)}, default=str)


@tool(
    name="aws_cognito_describe_user_pool",
    description="Get detailed configuration for a Cognito user pool.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "user_pool_id": {
                "type": "string",
                "description": "User pool ID",
            },
        },
        "required": ["user_pool_id"],
    },
    is_read_only=True,
)
async def describe_user_pool(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cognito-idp", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_user_pool(
            UserPoolId=arguments["user_pool_id"]
        )
        return response.get("UserPool", {})

    pool = await asyncio.to_thread(_execute)
    return json.dumps({"user_pool": pool}, default=str)


@tool(
    name="aws_cognito_list_users",
    description="List users in a Cognito user pool with optional filter.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "user_pool_id": {
                "type": "string",
                "description": "User pool ID",
            },
            "filter": {
                "type": "string",
                "description": "Filter expression (e.g., 'email = \"user@example.com\"', 'status = \"Enabled\"')",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum users to return (default: 60)",
            },
        },
        "required": ["user_pool_id"],
    },
    is_read_only=True,
)
async def list_users(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cognito-idp", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "UserPoolId": arguments["user_pool_id"],
            "Limit": arguments.get("limit", 60),
        }
        if "filter" in arguments:
            kwargs["Filter"] = arguments["filter"]

        response = client.list_users(**kwargs)
        return response.get("Users", [])

    users = await asyncio.to_thread(_execute)
    return json.dumps({"users": users, "count": len(users)}, default=str)


@tool(
    name="aws_cognito_list_groups",
    description="List groups in a Cognito user pool.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "user_pool_id": {
                "type": "string",
                "description": "User pool ID",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum groups to return (default: 60)",
            },
        },
        "required": ["user_pool_id"],
    },
    is_read_only=True,
)
async def list_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cognito-idp", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_groups(
            UserPoolId=arguments["user_pool_id"],
            Limit=arguments.get("limit", 60),
        )
        return response.get("Groups", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"groups": groups, "count": len(groups)}, default=str)
