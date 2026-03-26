"""DocumentDB tools: clusters and instances."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_docdb_describe_db_clusters",
    description="Describe DocumentDB clusters.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "db_cluster_identifier": {
                "type": "string",
                "description": "Specific cluster identifier (optional)",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Values": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["Name", "Values"],
                },
                "description": "API filters",
            },
        },
    },
    is_read_only=True,
)
async def describe_db_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client("docdb", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "db_cluster_identifier" in arguments:
            kwargs["DBClusterIdentifier"] = arguments["db_cluster_identifier"]
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]

        response = client.describe_db_clusters(**kwargs)
        return response.get("DBClusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps(
        {"db_clusters": clusters, "count": len(clusters)}, default=str
    )


@tool(
    name="aws_docdb_describe_db_instances",
    description="Describe DocumentDB instances.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "db_instance_identifier": {
                "type": "string",
                "description": "Specific instance identifier (optional)",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Values": {"type": "array", "items": {"type": "string"}},
                    },
                    "required": ["Name", "Values"],
                },
                "description": "API filters (e.g., db-cluster-id)",
            },
        },
    },
    is_read_only=True,
)
async def describe_db_instances(arguments: dict) -> str:
    def _execute():
        client = get_client("docdb", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "db_instance_identifier" in arguments:
            kwargs["DBInstanceIdentifier"] = arguments["db_instance_identifier"]
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]

        response = client.describe_db_instances(**kwargs)
        return response.get("DBInstances", [])

    instances = await asyncio.to_thread(_execute)
    return json.dumps(
        {"db_instances": instances, "count": len(instances)}, default=str
    )
