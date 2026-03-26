"""CodeBuild tools: projects and builds."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_codebuild_list_projects",
    description="List CodeBuild project names.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "sort_by": {
                "type": "string",
                "enum": ["NAME", "CREATED_TIME", "LAST_MODIFIED_TIME"],
                "description": "Sort order (default: NAME)",
            },
            "sort_order": {
                "type": "string",
                "enum": ["ASCENDING", "DESCENDING"],
                "description": "Sort direction (default: ASCENDING)",
            },
        },
    },
    is_read_only=True,
)
async def list_projects(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codebuild", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "sortBy": arguments.get("sort_by", "NAME"),
            "sortOrder": arguments.get("sort_order", "ASCENDING"),
        }
        response = client.list_projects(**kwargs)
        return response.get("projects", [])

    projects = await asyncio.to_thread(_execute)
    return json.dumps({"projects": projects, "count": len(projects)}, default=str)


@tool(
    name="aws_codebuild_batch_get_projects",
    description="Get full configuration details for one or more CodeBuild projects.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Project names to retrieve (max 100)",
            },
        },
        "required": ["names"],
    },
    is_read_only=True,
)
async def batch_get_projects(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codebuild", arguments.get("profile"), arguments.get("region")
        )
        response = client.batch_get_projects(names=arguments["names"])
        return response.get("projects", [])

    projects = await asyncio.to_thread(_execute)
    return json.dumps({"projects": projects, "count": len(projects)}, default=str)


@tool(
    name="aws_codebuild_list_builds_for_project",
    description="List recent build IDs for a CodeBuild project.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "project_name": {
                "type": "string",
                "description": "CodeBuild project name",
            },
            "sort_order": {
                "type": "string",
                "enum": ["ASCENDING", "DESCENDING"],
                "description": "Sort order (default: DESCENDING — most recent first)",
            },
        },
        "required": ["project_name"],
    },
    is_read_only=True,
)
async def list_builds_for_project(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codebuild", arguments.get("profile"), arguments.get("region")
        )
        response = client.list_builds_for_project(
            projectName=arguments["project_name"],
            sortOrder=arguments.get("sort_order", "DESCENDING"),
        )
        return response.get("ids", [])

    build_ids = await asyncio.to_thread(_execute)
    return json.dumps({"build_ids": build_ids, "count": len(build_ids)}, default=str)


@tool(
    name="aws_codebuild_batch_get_builds",
    description="Get full details (status, logs, duration, phases) for CodeBuild builds.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Build IDs to retrieve (max 100)",
            },
        },
        "required": ["ids"],
    },
    is_read_only=True,
)
async def batch_get_builds(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "codebuild", arguments.get("profile"), arguments.get("region")
        )
        response = client.batch_get_builds(ids=arguments["ids"])
        return response.get("builds", [])

    builds = await asyncio.to_thread(_execute)
    return json.dumps({"builds": builds, "count": len(builds)}, default=str)
