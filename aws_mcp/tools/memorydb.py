"""MemoryDB tools: clusters, snapshots, and ACLs."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_memorydb_describe_clusters",
    description="Describe MemoryDB for Redis clusters.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_name": {
                "type": "string",
                "description": "Specific cluster name (optional)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum clusters to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "memorydb", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "cluster_name" in arguments:
            kwargs["ClusterName"] = arguments["cluster_name"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.describe_clusters(**kwargs)
        return response.get("Clusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps(
        {"clusters": clusters, "count": len(clusters)}, default=str
    )


@tool(
    name="aws_memorydb_describe_snapshots",
    description="Describe MemoryDB snapshots.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_name": {
                "type": "string",
                "description": "Filter by cluster name",
            },
            "snapshot_name": {
                "type": "string",
                "description": "Specific snapshot name",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum snapshots to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_snapshots(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "memorydb", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "cluster_name" in arguments:
            kwargs["ClusterName"] = arguments["cluster_name"]
        if "snapshot_name" in arguments:
            kwargs["SnapshotName"] = arguments["snapshot_name"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.describe_snapshots(**kwargs)
        return response.get("Snapshots", [])

    snapshots = await asyncio.to_thread(_execute)
    return json.dumps(
        {"snapshots": snapshots, "count": len(snapshots)}, default=str
    )
