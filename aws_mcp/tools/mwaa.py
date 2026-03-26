"""MWAA (Managed Workflows for Apache Airflow) tools."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_mwaa_list_environments",
    description="List MWAA (Apache Airflow) environments.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum environments to return",
            },
        },
    },
    is_read_only=True,
)
async def list_environments(arguments: dict) -> str:
    def _execute():
        client = get_client("mwaa", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_environments(**kwargs)
        return response.get("Environments", [])

    envs = await asyncio.to_thread(_execute)
    return json.dumps({"environments": envs, "count": len(envs)}, default=str)


@tool(
    name="aws_mwaa_get_environment",
    description=(
        "Get detailed MWAA environment info: Airflow version, DAG S3 path, "
        "execution role, network config, logging, status, and web server URL."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "MWAA environment name",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def get_environment(arguments: dict) -> str:
    def _execute():
        client = get_client("mwaa", arguments.get("profile"), arguments.get("region"))
        response = client.get_environment(Name=arguments["name"])
        return response.get("Environment", {})

    env = await asyncio.to_thread(_execute)
    return json.dumps({"environment": env}, default=str)
