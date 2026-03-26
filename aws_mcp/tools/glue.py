"""Glue tools: databases, tables, jobs, and crawlers."""
import asyncio
import json

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_glue_get_databases",
    description="List Glue Data Catalog databases.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "catalog_id": {
                "type": "string",
                "description": "Catalog ID (default: account ID)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum databases to return",
            },
        },
    },
    is_read_only=True,
)
async def get_databases(arguments: dict) -> str:
    def _execute():
        client = get_client("glue", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "catalog_id" in arguments:
            kwargs["CatalogId"] = arguments["catalog_id"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_databases(**kwargs)
        return response.get("DatabaseList", [])

    databases = await asyncio.to_thread(_execute)
    return json.dumps(
        {"databases": databases, "count": len(databases)}, default=str
    )


@tool(
    name="aws_glue_get_tables",
    description="List tables in a Glue Data Catalog database.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "database_name": {
                "type": "string",
                "description": "Glue database name",
            },
            "expression": {
                "type": "string",
                "description": "Regular expression filter on table names",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum tables to return",
            },
        },
        "required": ["database_name"],
    },
    is_read_only=True,
)
async def get_tables(arguments: dict) -> str:
    def _execute():
        client = get_client("glue", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"DatabaseName": arguments["database_name"]}
        if "expression" in arguments:
            kwargs["Expression"] = arguments["expression"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_tables(**kwargs)
        return response.get("TableList", [])

    tables = await asyncio.to_thread(_execute)
    return json.dumps({"tables": tables, "count": len(tables)}, default=str)


@tool(
    name="aws_glue_get_jobs",
    description="List Glue ETL jobs.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum jobs to return",
            },
        },
    },
    is_read_only=True,
)
async def get_jobs(arguments: dict) -> str:
    def _execute():
        client = get_client("glue", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_jobs(**kwargs)
        return response.get("Jobs", [])

    jobs = await asyncio.to_thread(_execute)
    return json.dumps({"jobs": jobs, "count": len(jobs)}, default=str)


@tool(
    name="aws_glue_get_job_runs",
    description="Get execution history for a Glue job.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "job_name": {
                "type": "string",
                "description": "Glue job name",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum runs to return",
            },
        },
        "required": ["job_name"],
    },
    is_read_only=True,
)
async def get_job_runs(arguments: dict) -> str:
    def _execute():
        client = get_client("glue", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"JobName": arguments["job_name"]}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_job_runs(**kwargs)
        return response.get("JobRuns", [])

    runs = await asyncio.to_thread(_execute)
    return json.dumps({"job_runs": runs, "count": len(runs)}, default=str)


@tool(
    name="aws_glue_get_crawlers",
    description="List Glue crawlers.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum crawlers to return",
            },
        },
    },
    is_read_only=True,
)
async def get_crawlers(arguments: dict) -> str:
    def _execute():
        client = get_client("glue", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_crawlers(**kwargs)
        return response.get("Crawlers", [])

    crawlers = await asyncio.to_thread(_execute)
    return json.dumps(
        {"crawlers": crawlers, "count": len(crawlers)}, default=str
    )


@tool(
    name="aws_glue_start_job_run",
    description="Start a Glue job run. Blocked in --readonly mode.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "job_name": {
                "type": "string",
                "description": "Glue job name",
            },
            "arguments": {
                "type": "object",
                "description": "Job arguments as key-value pairs",
            },
        },
        "required": ["job_name"],
    },
    is_read_only=False,
)
async def start_job_run(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: Glue StartJobRun is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("glue", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"JobName": arguments["job_name"]}
        if "arguments" in arguments:
            kwargs["Arguments"] = arguments["arguments"]

        response = client.start_job_run(**kwargs)
        return {"JobRunId": response.get("JobRunId")}

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
