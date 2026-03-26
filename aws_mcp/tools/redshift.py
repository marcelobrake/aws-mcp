"""Redshift tools: clusters, snapshots, and queries."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_redshift_describe_clusters",
    description="List Redshift clusters with their configuration, status, and endpoint.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_identifier": {
                "type": "string",
                "description": "Specific cluster identifier (optional — returns all if omitted)",
            },
            "max_records": {
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
            "redshift", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "cluster_identifier" in arguments:
            kwargs["ClusterIdentifier"] = arguments["cluster_identifier"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]
        response = client.describe_clusters(**kwargs)
        return response.get("Clusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps({"clusters": clusters, "count": len(clusters)}, default=str)


@tool(
    name="aws_redshift_describe_cluster_snapshots",
    description="List Redshift cluster snapshots (manual and automated).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_identifier": {
                "type": "string",
                "description": "Filter by cluster identifier",
            },
            "snapshot_type": {
                "type": "string",
                "enum": ["automated", "manual", "shared", "awsbackup"],
                "description": "Filter by snapshot type",
            },
            "max_records": {
                "type": "integer",
                "description": "Maximum snapshots to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_cluster_snapshots(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "redshift", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "cluster_identifier" in arguments:
            kwargs["ClusterIdentifier"] = arguments["cluster_identifier"]
        if "snapshot_type" in arguments:
            kwargs["SnapshotType"] = arguments["snapshot_type"]
        if "max_records" in arguments:
            kwargs["MaxRecords"] = arguments["max_records"]
        response = client.describe_cluster_snapshots(**kwargs)
        return response.get("Snapshots", [])

    snapshots = await asyncio.to_thread(_execute)
    return json.dumps({"snapshots": snapshots, "count": len(snapshots)}, default=str)


@tool(
    name="aws_redshift_describe_cluster_parameters",
    description="List parameters for a Redshift parameter group.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "parameter_group_name": {
                "type": "string",
                "description": "Parameter group name",
            },
            "source": {
                "type": "string",
                "enum": ["user", "engine-default"],
                "description": "Filter by source (user-modified or engine defaults)",
            },
        },
        "required": ["parameter_group_name"],
    },
    is_read_only=True,
)
async def describe_cluster_parameters(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "redshift", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"ParameterGroupName": arguments["parameter_group_name"]}
        if "source" in arguments:
            kwargs["Source"] = arguments["source"]
        response = client.describe_cluster_parameters(**kwargs)
        return response.get("Parameters", [])

    params = await asyncio.to_thread(_execute)
    return json.dumps({"parameters": params, "count": len(params)}, default=str)
