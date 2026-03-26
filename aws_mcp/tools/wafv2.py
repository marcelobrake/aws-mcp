"""WAF v2 tools: Web ACLs, IP sets, and rule groups."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_wafv2_list_web_acls",
    description=(
        "List WAF v2 Web ACLs. Scope must be 'REGIONAL' (ALB, API GW, AppSync) "
        "or 'CLOUDFRONT' (must use us-east-1 region)."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "scope": {
                "type": "string",
                "enum": ["REGIONAL", "CLOUDFRONT"],
                "description": "REGIONAL for ALB/API Gateway, CLOUDFRONT for CloudFront distributions",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum Web ACLs to return (default: 100)",
            },
        },
        "required": ["scope"],
    },
    is_read_only=True,
)
async def list_web_acls(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "wafv2", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "Scope": arguments["scope"],
            "Limit": arguments.get("limit", 100),
        }
        response = client.list_web_acls(**kwargs)
        return response.get("WebACLs", [])

    acls = await asyncio.to_thread(_execute)
    return json.dumps({"web_acls": acls, "count": len(acls)}, default=str)


@tool(
    name="aws_wafv2_get_web_acl",
    description="Get the full configuration of a WAF v2 Web ACL including all rules.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Web ACL name",
            },
            "scope": {
                "type": "string",
                "enum": ["REGIONAL", "CLOUDFRONT"],
                "description": "REGIONAL or CLOUDFRONT",
            },
            "id": {
                "type": "string",
                "description": "Web ACL ID",
            },
        },
        "required": ["name", "scope", "id"],
    },
    is_read_only=True,
)
async def get_web_acl(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "wafv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_web_acl(
            Name=arguments["name"],
            Scope=arguments["scope"],
            Id=arguments["id"],
        )
        return response.get("WebACL", {})

    acl = await asyncio.to_thread(_execute)
    return json.dumps({"web_acl": acl}, default=str)


@tool(
    name="aws_wafv2_list_ip_sets",
    description="List WAF v2 IP sets (allow/block lists).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "scope": {
                "type": "string",
                "enum": ["REGIONAL", "CLOUDFRONT"],
                "description": "REGIONAL or CLOUDFRONT",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum IP sets to return (default: 100)",
            },
        },
        "required": ["scope"],
    },
    is_read_only=True,
)
async def list_ip_sets(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "wafv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_ip_sets(
            Scope=arguments["scope"],
            Limit=arguments.get("limit", 100),
        )
        return response.get("IPSets", [])

    ip_sets = await asyncio.to_thread(_execute)
    return json.dumps({"ip_sets": ip_sets, "count": len(ip_sets)}, default=str)


@tool(
    name="aws_wafv2_list_rule_groups",
    description="List WAF v2 managed and custom rule groups.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "scope": {
                "type": "string",
                "enum": ["REGIONAL", "CLOUDFRONT"],
                "description": "REGIONAL or CLOUDFRONT",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum rule groups to return (default: 100)",
            },
        },
        "required": ["scope"],
    },
    is_read_only=True,
)
async def list_rule_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "wafv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_rule_groups(
            Scope=arguments["scope"],
            Limit=arguments.get("limit", 100),
        )
        return response.get("RuleGroups", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"rule_groups": groups, "count": len(groups)}, default=str)


@tool(
    name="aws_wafv2_get_web_acl_for_resource",
    description="Get the Web ACL associated with an AWS resource (ALB, API GW, AppSync).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "resource_arn": {
                "type": "string",
                "description": "ARN of the resource (ALB, API Gateway stage, AppSync GraphQL API)",
            },
        },
        "required": ["resource_arn"],
    },
    is_read_only=True,
)
async def get_web_acl_for_resource(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "wafv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_web_acl_for_resource(
            ResourceArn=arguments["resource_arn"]
        )
        return response.get("WebACL")

    acl = await asyncio.to_thread(_execute)
    return json.dumps({"web_acl": acl}, default=str)
