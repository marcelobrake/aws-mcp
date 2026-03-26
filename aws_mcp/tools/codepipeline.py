"""CodePipeline tools: pipelines, executions, and state."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_codepipeline_list_pipelines",
    description="List CodePipeline pipelines.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum pipelines to return",
            },
        },
    },
    is_read_only=True,
)
async def list_pipelines(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codepipeline", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]
        response = client.list_pipelines(**kwargs)
        return response.get("pipelines", [])

    pipelines = await asyncio.to_thread(_execute)
    return json.dumps({"pipelines": pipelines, "count": len(pipelines)}, default=str)


@tool(
    name="aws_codepipeline_get_pipeline",
    description="Get the full structure and stage configuration of a CodePipeline.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Pipeline name",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def get_pipeline(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codepipeline", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_pipeline(name=arguments["name"])
        return response.get("pipeline", {})

    pipeline = await asyncio.to_thread(_execute)
    return json.dumps({"pipeline": pipeline}, default=str)


@tool(
    name="aws_codepipeline_get_pipeline_state",
    description="Get the current execution state of each stage in a CodePipeline.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Pipeline name",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def get_pipeline_state(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codepipeline", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_pipeline_state(name=arguments["name"])
        response.pop("ResponseMetadata", None)
        return response

    state = await asyncio.to_thread(_execute)
    return json.dumps(state, default=str)


@tool(
    name="aws_codepipeline_list_pipeline_executions",
    description="List recent executions of a CodePipeline with their status.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "pipeline_name": {
                "type": "string",
                "description": "Pipeline name",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum executions to return (default: 10)",
            },
        },
        "required": ["pipeline_name"],
    },
    is_read_only=True,
)
async def list_pipeline_executions(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codepipeline", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_pipeline_executions(
            pipelineName=arguments["pipeline_name"],
            maxResults=arguments.get("max_results", 10),
        )
        return response.get("pipelineExecutionSummaries", [])

    executions = await asyncio.to_thread(_execute)
    return json.dumps({"executions": executions, "count": len(executions)}, default=str)
