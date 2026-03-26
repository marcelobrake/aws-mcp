"""OpenSearch tools: domains and cluster health."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_opensearch_list_domain_names",
    description="List all OpenSearch domain names in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "engine_type": {
                "type": "string",
                "enum": ["OpenSearch", "Elasticsearch"],
                "description": "Filter by engine type (optional)",
            },
        },
    },
    is_read_only=True,
)
async def list_domain_names(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "opensearch", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "engine_type" in arguments:
            kwargs["EngineType"] = arguments["engine_type"]

        response = client.list_domain_names(**kwargs)
        return response.get("DomainNames", [])

    domains = await asyncio.to_thread(_execute)
    return json.dumps({"domains": domains, "count": len(domains)}, default=str)


@tool(
    name="aws_opensearch_describe_domain",
    description=(
        "Get detailed configuration for an OpenSearch domain: cluster config, "
        "EBS, VPC, endpoints, engine version, and status."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "domain_name": {
                "type": "string",
                "description": "OpenSearch domain name",
            },
        },
        "required": ["domain_name"],
    },
    is_read_only=True,
)
async def describe_domain(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "opensearch", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_domain(
            DomainName=arguments["domain_name"]
        )
        return response.get("DomainStatus", {})

    domain = await asyncio.to_thread(_execute)
    return json.dumps({"domain_status": domain}, default=str)


@tool(
    name="aws_opensearch_describe_domain_health",
    description="Get health status of an OpenSearch domain (cluster health, node count, shards).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "domain_name": {
                "type": "string",
                "description": "OpenSearch domain name",
            },
        },
        "required": ["domain_name"],
    },
    is_read_only=True,
)
async def describe_domain_health(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "opensearch", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_domain_health(
            DomainName=arguments["domain_name"]
        )
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
