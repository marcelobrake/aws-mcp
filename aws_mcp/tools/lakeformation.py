"""Lake Formation tools: permissions and data lake settings."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_lakeformation_get_data_lake_settings",
    description="Get Lake Formation data lake settings (admins, create defaults, etc.).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "catalog_id": {
                "type": "string",
                "description": "Catalog ID (default: account ID)",
            },
        },
    },
    is_read_only=True,
)
async def get_data_lake_settings(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "lakeformation", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "catalog_id" in arguments:
            kwargs["CatalogId"] = arguments["catalog_id"]

        response = client.get_data_lake_settings(**kwargs)
        return response.get("DataLakeSettings", {})

    settings = await asyncio.to_thread(_execute)
    return json.dumps({"data_lake_settings": settings}, default=str)


@tool(
    name="aws_lakeformation_list_permissions",
    description="List Lake Formation permissions for a principal or resource.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "catalog_id": {
                "type": "string",
                "description": "Catalog ID (default: account ID)",
            },
            "principal": {
                "type": "object",
                "properties": {
                    "DataLakePrincipalIdentifier": {"type": "string"},
                },
                "description": "Filter by principal (IAM ARN)",
            },
            "resource_type": {
                "type": "string",
                "enum": ["CATALOG", "DATABASE", "TABLE", "DATA_LOCATION", "LF_TAG", "LF_TAG_POLICY"],
                "description": "Filter by resource type",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum permissions to return",
            },
        },
    },
    is_read_only=True,
)
async def list_permissions(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "lakeformation", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "catalog_id" in arguments:
            kwargs["CatalogId"] = arguments["catalog_id"]
        if "principal" in arguments:
            kwargs["Principal"] = arguments["principal"]
        if "resource_type" in arguments:
            kwargs["ResourceType"] = arguments["resource_type"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_permissions(**kwargs)
        return response.get("PrincipalResourcePermissions", [])

    perms = await asyncio.to_thread(_execute)
    return json.dumps(
        {"permissions": perms, "count": len(perms)}, default=str
    )


@tool(
    name="aws_lakeformation_list_resources",
    description="List resources registered with Lake Formation.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum resources to return",
            },
        },
    },
    is_read_only=True,
)
async def list_resources(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "lakeformation", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_resources(**kwargs)
        return response.get("ResourceInfoList", [])

    resources = await asyncio.to_thread(_execute)
    return json.dumps(
        {"resources": resources, "count": len(resources)}, default=str
    )
