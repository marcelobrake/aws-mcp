"""Organizations tools: organization, accounts, and OUs."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_organizations_describe_organization",
    description="Describe the AWS Organization (master account, feature set, ARN).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def describe_organization(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "organizations", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_organization()
        return response.get("Organization", {})

    org = await asyncio.to_thread(_execute)
    return json.dumps({"organization": org}, default=str)


@tool(
    name="aws_organizations_list_accounts",
    description="List all AWS accounts in the organization.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_accounts(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "organizations", arguments.get("profile"), arguments.get("region")
        )
        accounts = []
        paginator = client.get_paginator("list_accounts")
        for page in paginator.paginate():
            accounts.extend(page.get("Accounts", []))
        return accounts

    accounts = await asyncio.to_thread(_execute)
    return json.dumps({"accounts": accounts, "count": len(accounts)}, default=str)


@tool(
    name="aws_organizations_list_organizational_units",
    description="List organizational units (OUs) for a parent (root or OU).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "parent_id": {
                "type": "string",
                "description": "Parent ID (root ID like 'r-xxxx' or OU ID like 'ou-xxxx-yyyyyyyy')",
            },
        },
        "required": ["parent_id"],
    },
    is_read_only=True,
)
async def list_organizational_units(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "organizations", arguments.get("profile"), arguments.get("region")
        )
        ous = []
        paginator = client.get_paginator("list_organizational_units_for_parent")
        for page in paginator.paginate(ParentId=arguments["parent_id"]):
            ous.extend(page.get("OrganizationalUnits", []))
        return ous

    ous = await asyncio.to_thread(_execute)
    return json.dumps({"organizational_units": ous, "count": len(ous)}, default=str)


@tool(
    name="aws_organizations_list_roots",
    description="List the root(s) of the AWS Organization (needed to navigate the OU tree).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def list_roots(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "organizations", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_roots()
        return response.get("Roots", [])

    roots = await asyncio.to_thread(_execute)
    return json.dumps({"roots": roots, "count": len(roots)}, default=str)
