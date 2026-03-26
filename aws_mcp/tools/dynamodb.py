"""DynamoDB tools: tables, queries, and scans."""
import asyncio
import json

from boto3.dynamodb.types import TypeDeserializer

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool

_deserializer = TypeDeserializer()


def _deserialize_item(item: dict) -> dict:
    """Convert DynamoDB-format item to plain Python dict."""
    return {k: _deserializer.deserialize(v) for k, v in item.items()}


def _deserialize_items(items: list[dict]) -> list[dict]:
    """Convert a list of DynamoDB items."""
    return [_deserialize_item(item) for item in items]


@tool(
    name="aws_dynamodb_list_tables",
    description="List DynamoDB tables in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "limit": {
                "type": "integer",
                "description": "Maximum number of tables to return (default: 100)",
            },
        },
    },
    is_read_only=True,
)
async def list_tables(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "dynamodb", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "limit" in arguments:
            kwargs["Limit"] = arguments["limit"]

        response = client.list_tables(**kwargs)
        return response.get("TableNames", [])

    tables = await asyncio.to_thread(_execute)
    return json.dumps({"tables": tables, "count": len(tables)}, default=str)


@tool(
    name="aws_dynamodb_describe_table",
    description="Get schema, throughput, indexes, and status for a DynamoDB table.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "table_name": {
                "type": "string",
                "description": "DynamoDB table name",
            },
        },
        "required": ["table_name"],
    },
    is_read_only=True,
)
async def describe_table(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "dynamodb", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_table(TableName=arguments["table_name"])
        table = response.get("Table", {})
        return table

    table = await asyncio.to_thread(_execute)
    return json.dumps({"table": table}, default=str)


@tool(
    name="aws_dynamodb_query",
    description=(
        "Query a DynamoDB table using a key condition expression. "
        "Items are returned deserialized as plain JSON objects."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "table_name": {
                "type": "string",
                "description": "DynamoDB table name",
            },
            "key_condition_expression": {
                "type": "string",
                "description": "Key condition (e.g., 'pk = :pkval AND begins_with(sk, :skprefix)')",
            },
            "expression_attribute_values": {
                "type": "object",
                "description": (
                    "Values for expression placeholders in DynamoDB format "
                    "(e.g., {\":pkval\": {\"S\": \"user#123\"}})"
                ),
            },
            "expression_attribute_names": {
                "type": "object",
                "description": "Name placeholders for reserved words (e.g., {\"#s\": \"status\"})",
            },
            "filter_expression": {
                "type": "string",
                "description": "Additional filter applied after the query",
            },
            "index_name": {
                "type": "string",
                "description": "Name of a GSI or LSI to query",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum items to evaluate",
            },
            "scan_index_forward": {
                "type": "boolean",
                "description": "True for ascending order, False for descending (default: True)",
            },
        },
        "required": ["table_name", "key_condition_expression", "expression_attribute_values"],
    },
    is_read_only=True,
)
async def query_table(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "dynamodb", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "TableName": arguments["table_name"],
            "KeyConditionExpression": arguments["key_condition_expression"],
            "ExpressionAttributeValues": arguments["expression_attribute_values"],
        }
        if "expression_attribute_names" in arguments:
            kwargs["ExpressionAttributeNames"] = arguments["expression_attribute_names"]
        if "filter_expression" in arguments:
            kwargs["FilterExpression"] = arguments["filter_expression"]
        if "index_name" in arguments:
            kwargs["IndexName"] = arguments["index_name"]
        if "limit" in arguments:
            kwargs["Limit"] = arguments["limit"]
        if "scan_index_forward" in arguments:
            kwargs["ScanIndexForward"] = arguments["scan_index_forward"]

        response = client.query(**kwargs)
        items = _deserialize_items(response.get("Items", []))
        return {
            "items": items,
            "count": response.get("Count", 0),
            "scanned_count": response.get("ScannedCount", 0),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_dynamodb_scan",
    description=(
        "Scan a DynamoDB table (reads every item). Use sparingly on large tables. "
        "Prefer query when you know the partition key."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "table_name": {
                "type": "string",
                "description": "DynamoDB table name",
            },
            "filter_expression": {
                "type": "string",
                "description": "Filter expression (e.g., '#s = :val')",
            },
            "expression_attribute_values": {
                "type": "object",
                "description": "Values in DynamoDB format (e.g., {\":val\": {\"S\": \"active\"}})",
            },
            "expression_attribute_names": {
                "type": "object",
                "description": "Name placeholders (e.g., {\"#s\": \"status\"})",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum items to evaluate (default: 100)",
            },
        },
        "required": ["table_name"],
    },
    is_read_only=True,
)
async def scan_table(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "dynamodb", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "TableName": arguments["table_name"],
            "Limit": arguments.get("limit", 100),
        }
        if "filter_expression" in arguments:
            kwargs["FilterExpression"] = arguments["filter_expression"]
        if "expression_attribute_values" in arguments:
            kwargs["ExpressionAttributeValues"] = arguments["expression_attribute_values"]
        if "expression_attribute_names" in arguments:
            kwargs["ExpressionAttributeNames"] = arguments["expression_attribute_names"]

        response = client.scan(**kwargs)
        items = _deserialize_items(response.get("Items", []))
        return {
            "items": items,
            "count": response.get("Count", 0),
            "scanned_count": response.get("ScannedCount", 0),
        }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
