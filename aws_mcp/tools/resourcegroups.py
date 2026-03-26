"""Resource Groups and Tag Manager tools: tag-based resource discovery."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_tagging_get_resources",
    description=(
        "Find resources by tag across all supported AWS services. "
        "Uses the Resource Groups Tagging API."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "tag_filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Key": {"type": "string"},
                        "Values": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["Key"],
                },
                "description": 'Tag filters (e.g., [{"Key": "Environment", "Values": ["prod"]}])',
            },
            "resource_type_filters": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "Filter by resource type (e.g., ['ec2:instance', 's3:bucket', 'lambda:function'])"
                ),
            },
            "resources_per_page": {
                "type": "integer",
                "description": "Number of resources per page (max 100, default 50)",
            },
        },
    },
    is_read_only=True,
)
async def get_resources(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "resourcegroupstaggingapi", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "ResourcesPerPage": arguments.get("resources_per_page", 50),
        }
        if "tag_filters" in arguments:
            kwargs["TagFilters"] = arguments["tag_filters"]
        if "resource_type_filters" in arguments:
            kwargs["ResourceTypeFilters"] = arguments["resource_type_filters"]

        resources = []
        paginator = client.get_paginator("get_resources")
        for page in paginator.paginate(**kwargs):
            resources.extend(page.get("ResourceTagMappingList", []))
        return resources

    resources = await asyncio.to_thread(_execute)
    return json.dumps({"resources": resources, "count": len(resources)}, default=str)


@tool(
    name="aws_tagging_get_tag_keys",
    description="List all tag keys used across AWS resources in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def get_tag_keys(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "resourcegroupstaggingapi", arguments.get("profile"), arguments.get("region")
        )
        keys = []
        paginator = client.get_paginator("get_tag_keys")
        for page in paginator.paginate():
            keys.extend(page.get("TagKeys", []))
        return keys

    keys = await asyncio.to_thread(_execute)
    return json.dumps({"tag_keys": keys, "count": len(keys)}, default=str)


@tool(
    name="aws_tagging_get_tag_values",
    description="List all values used for a specific tag key across resources.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "key": {
                "type": "string",
                "description": "Tag key to retrieve values for",
            },
        },
        "required": ["key"],
    },
    is_read_only=True,
)
async def get_tag_values(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "resourcegroupstaggingapi", arguments.get("profile"), arguments.get("region")
        )
        values = []
        paginator = client.get_paginator("get_tag_values")
        for page in paginator.paginate(Key=arguments["key"]):
            values.extend(page.get("TagValues", []))
        return values

    values = await asyncio.to_thread(_execute)
    return json.dumps({"tag_values": values, "count": len(values)}, default=str)


@tool(
    name="aws_resourcegroups_list_groups",
    description="List Resource Groups in the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum groups to return",
            },
        },
    },
    is_read_only=True,
)
async def list_groups(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "resource-groups", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        response = client.list_groups(**kwargs)
        return response.get("GroupIdentifiers", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"groups": groups, "count": len(groups)}, default=str)
