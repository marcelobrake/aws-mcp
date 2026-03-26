"""RDS tools: database instance information."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_rds_describe_db_instances",
    description=(
        "Describe RDS database instances. Returns engine, status, endpoint, "
        "size, and storage details for each instance."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "db_instance_identifier": {
                "type": "string",
                "description": "Specific DB instance identifier to describe",
            },
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Name": {"type": "string"},
                        "Values": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["Name", "Values"],
                },
                "description": "RDS API filters (e.g., engine, db-cluster-id)",
            },
        },
    },
    is_read_only=True,
)
async def describe_db_instances(arguments: dict) -> str:
    def _execute():
        client = get_client("rds", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "db_instance_identifier" in arguments:
            kwargs["DBInstanceIdentifier"] = arguments["db_instance_identifier"]
        if "filters" in arguments:
            kwargs["Filters"] = arguments["filters"]

        response = client.describe_db_instances(**kwargs)
        instances = response.get("DBInstances", [])
        return instances

    instances = await asyncio.to_thread(_execute)
    return json.dumps(
        {"db_instances": instances, "count": len(instances)}, default=str
    )


@tool(
    name="aws_rds_describe_db_clusters",
    description="Describe RDS Aurora database clusters.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "db_cluster_identifier": {
                "type": "string",
                "description": "Specific DB cluster identifier to describe",
            },
        },
    },
    is_read_only=True,
)
async def describe_db_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client("rds", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "db_cluster_identifier" in arguments:
            kwargs["DBClusterIdentifier"] = arguments["db_cluster_identifier"]

        response = client.describe_db_clusters(**kwargs)
        clusters = response.get("DBClusters", [])
        return clusters

    clusters = await asyncio.to_thread(_execute)
    return json.dumps(
        {"db_clusters": clusters, "count": len(clusters)}, default=str
    )
