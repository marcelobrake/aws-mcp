"""EMR tools: clusters, steps, and instances."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_emr_list_clusters",
    description="List EMR clusters in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_states": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "STARTING",
                        "BOOTSTRAPPING",
                        "RUNNING",
                        "WAITING",
                        "TERMINATING",
                        "TERMINATED",
                        "TERMINATED_WITH_ERRORS",
                    ],
                },
                "description": "Filter by cluster states",
            },
        },
    },
    is_read_only=True,
)
async def list_clusters(arguments: dict) -> str:
    def _execute():
        client = get_client("emr", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "cluster_states" in arguments:
            kwargs["ClusterStates"] = arguments["cluster_states"]
        response = client.list_clusters(**kwargs)
        return response.get("Clusters", [])

    clusters = await asyncio.to_thread(_execute)
    return json.dumps({"clusters": clusters, "count": len(clusters)}, default=str)


@tool(
    name="aws_emr_describe_cluster",
    description="Get detailed information about an EMR cluster.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_id": {
                "type": "string",
                "description": "Cluster ID (e.g., j-XXXXX)",
            },
        },
        "required": ["cluster_id"],
    },
    is_read_only=True,
)
async def describe_cluster(arguments: dict) -> str:
    def _execute():
        client = get_client("emr", arguments.get("profile"), arguments.get("region"))
        response = client.describe_cluster(ClusterId=arguments["cluster_id"])
        return response.get("Cluster", {})

    cluster = await asyncio.to_thread(_execute)
    return json.dumps({"cluster": cluster}, default=str)


@tool(
    name="aws_emr_list_steps",
    description="List steps in an EMR cluster.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "cluster_id": {
                "type": "string",
                "description": "Cluster ID",
            },
            "step_states": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [
                        "PENDING",
                        "CANCEL_PENDING",
                        "RUNNING",
                        "COMPLETED",
                        "CANCELLED",
                        "FAILED",
                        "INTERRUPTED",
                    ],
                },
                "description": "Filter by step state",
            },
        },
        "required": ["cluster_id"],
    },
    is_read_only=True,
)
async def list_steps(arguments: dict) -> str:
    def _execute():
        client = get_client("emr", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"ClusterId": arguments["cluster_id"]}
        if "step_states" in arguments:
            kwargs["StepStates"] = arguments["step_states"]
        response = client.list_steps(**kwargs)
        return response.get("Steps", [])

    steps = await asyncio.to_thread(_execute)
    return json.dumps({"steps": steps, "count": len(steps)}, default=str)
