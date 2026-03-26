"""CloudFront tools: distributions and invalidations."""
import asyncio
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_cloudfront_list_distributions",
    description="List CloudFront distributions with domain names, origins, and status.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_items": {
                "type": "string",
                "description": "Maximum distributions to return (as string)",
            },
        },
    },
    is_read_only=True,
)
async def list_distributions(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudfront", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_distributions(**kwargs)
        dist_list = response.get("DistributionList", {})
        items = dist_list.get("Items", [])
        summaries = [
            {
                "Id": d["Id"],
                "DomainName": d["DomainName"],
                "Status": d["Status"],
                "Enabled": d["Enabled"],
                "Aliases": d.get("Aliases", {}).get("Items", []),
                "Origins": [
                    o["DomainName"]
                    for o in d.get("Origins", {}).get("Items", [])
                ],
                "Comment": d.get("Comment", ""),
                "PriceClass": d.get("PriceClass"),
                "HttpVersion": d.get("HttpVersion"),
            }
            for d in items
        ]
        return summaries

    distributions = await asyncio.to_thread(_execute)
    return json.dumps(
        {"distributions": distributions, "count": len(distributions)}, default=str
    )


@tool(
    name="aws_cloudfront_get_distribution",
    description="Get full configuration details for a CloudFront distribution.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "distribution_id": {
                "type": "string",
                "description": "CloudFront distribution ID",
            },
        },
        "required": ["distribution_id"],
    },
    is_read_only=True,
)
async def get_distribution(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudfront", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_distribution(Id=arguments["distribution_id"])
        dist = response.get("Distribution", {})
        return dist

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_cloudfront_list_invalidations",
    description="List recent cache invalidation requests for a CloudFront distribution.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "distribution_id": {
                "type": "string",
                "description": "CloudFront distribution ID",
            },
            "max_items": {
                "type": "string",
                "description": "Maximum invalidations to return (as string)",
            },
        },
        "required": ["distribution_id"],
    },
    is_read_only=True,
)
async def list_invalidations(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "cloudfront", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"DistributionId": arguments["distribution_id"]}
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_invalidations(**kwargs)
        inv_list = response.get("InvalidationList", {})
        return inv_list.get("Items", [])

    invalidations = await asyncio.to_thread(_execute)
    return json.dumps(
        {"invalidations": invalidations, "count": len(invalidations)}, default=str
    )


@tool(
    name="aws_cloudfront_create_invalidation",
    description=(
        "Create a cache invalidation for a CloudFront distribution. "
        "Blocked in --readonly mode."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "distribution_id": {
                "type": "string",
                "description": "CloudFront distribution ID",
            },
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "URL paths to invalidate (e.g., ['/*'] or ['/index.html', '/css/*'])",
            },
        },
        "required": ["distribution_id", "paths"],
    },
    is_read_only=False,
)
async def create_invalidation(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: CloudFront CreateInvalidation is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    import time

    def _execute():
        client = get_client(
            "cloudfront", arguments.get("profile"), arguments.get("region")
        )
        response = client.create_invalidation(
            DistributionId=arguments["distribution_id"],
            InvalidationBatch={
                "Paths": {
                    "Quantity": len(arguments["paths"]),
                    "Items": arguments["paths"],
                },
                "CallerReference": str(int(time.time())),
            },
        )
        inv = response.get("Invalidation", {})
        return {
            "Id": inv.get("Id"),
            "Status": inv.get("Status"),
            "CreateTime": inv.get("CreateTime"),
            "Paths": arguments["paths"],
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
