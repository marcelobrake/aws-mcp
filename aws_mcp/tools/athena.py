"""Athena tools: queries, catalogs, and databases."""
import asyncio
import json

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_athena_list_work_groups",
    description="List Athena workgroups.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum workgroups to return",
            },
        },
    },
    is_read_only=True,
)
async def list_work_groups(arguments: dict) -> str:
    def _execute():
        client = get_client("athena", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_work_groups(**kwargs)
        return response.get("WorkGroups", [])

    groups = await asyncio.to_thread(_execute)
    return json.dumps({"work_groups": groups, "count": len(groups)}, default=str)


@tool(
    name="aws_athena_list_databases",
    description="List databases in an Athena data catalog.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "catalog_name": {
                "type": "string",
                "description": "Data catalog name (default: AwsDataCatalog)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum databases to return",
            },
        },
    },
    is_read_only=True,
)
async def list_databases(arguments: dict) -> str:
    def _execute():
        client = get_client("athena", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "CatalogName": arguments.get("catalog_name", "AwsDataCatalog"),
        }
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_databases(**kwargs)
        return response.get("DatabaseList", [])

    databases = await asyncio.to_thread(_execute)
    return json.dumps(
        {"databases": databases, "count": len(databases)}, default=str
    )


@tool(
    name="aws_athena_list_table_metadata",
    description="List tables in an Athena database.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "catalog_name": {
                "type": "string",
                "description": "Data catalog name (default: AwsDataCatalog)",
            },
            "database_name": {
                "type": "string",
                "description": "Database name",
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
async def list_table_metadata(arguments: dict) -> str:
    def _execute():
        client = get_client("athena", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "CatalogName": arguments.get("catalog_name", "AwsDataCatalog"),
            "DatabaseName": arguments["database_name"],
        }
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_table_metadata(**kwargs)
        return response.get("TableMetadataList", [])

    tables = await asyncio.to_thread(_execute)
    return json.dumps({"tables": tables, "count": len(tables)}, default=str)


@tool(
    name="aws_athena_start_query_execution",
    description=(
        "Start an Athena SQL query execution. Blocked in --readonly mode. "
        "Returns a query execution ID to check results with get_query_results."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "query_string": {
                "type": "string",
                "description": "SQL query to execute",
            },
            "database": {
                "type": "string",
                "description": "Database context for the query",
            },
            "output_location": {
                "type": "string",
                "description": "S3 location for results (e.g., 's3://bucket/path/')",
            },
            "work_group": {
                "type": "string",
                "description": "Athena workgroup (default: primary)",
            },
        },
        "required": ["query_string"],
    },
    is_read_only=False,
)
async def start_query_execution(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: Athena StartQueryExecution is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("athena", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"QueryString": arguments["query_string"]}

        query_ctx: dict = {}
        if "database" in arguments:
            query_ctx["Database"] = arguments["database"]
        if query_ctx:
            kwargs["QueryExecutionContext"] = query_ctx

        if "output_location" in arguments:
            kwargs["ResultConfiguration"] = {
                "OutputLocation": arguments["output_location"]
            }

        if "work_group" in arguments:
            kwargs["WorkGroup"] = arguments["work_group"]

        response = client.start_query_execution(**kwargs)
        return {"QueryExecutionId": response.get("QueryExecutionId")}

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_athena_get_query_execution",
    description="Get status and details of an Athena query execution.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "query_execution_id": {
                "type": "string",
                "description": "Query execution ID",
            },
        },
        "required": ["query_execution_id"],
    },
    is_read_only=True,
)
async def get_query_execution(arguments: dict) -> str:
    def _execute():
        client = get_client("athena", arguments.get("profile"), arguments.get("region"))
        response = client.get_query_execution(
            QueryExecutionId=arguments["query_execution_id"]
        )
        return response.get("QueryExecution", {})

    execution = await asyncio.to_thread(_execute)
    return json.dumps({"query_execution": execution}, default=str)


@tool(
    name="aws_athena_get_query_results",
    description="Get results of a completed Athena query execution.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "query_execution_id": {
                "type": "string",
                "description": "Query execution ID",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum rows to return (default: 1000)",
            },
        },
        "required": ["query_execution_id"],
    },
    is_read_only=True,
)
async def get_query_results(arguments: dict) -> str:
    def _execute():
        client = get_client("athena", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "QueryExecutionId": arguments["query_execution_id"],
        }
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_query_results(**kwargs)
        return response.get("ResultSet", {})

    result_set = await asyncio.to_thread(_execute)
    return json.dumps({"result_set": result_set}, default=str)
