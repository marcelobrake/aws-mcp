"""API Gateway tools: REST APIs (v1) and HTTP/WebSocket APIs (v2)."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


# --- REST API (API Gateway v1) ---


@tool(
    name="aws_apigateway_get_rest_apis",
    description="List API Gateway REST APIs (v1).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "limit": {
                "type": "integer",
                "description": "Maximum APIs to return",
            },
        },
    },
    is_read_only=True,
)
async def get_rest_apis(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "apigateway", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "limit" in arguments:
            kwargs["limit"] = arguments["limit"]

        response = client.get_rest_apis(**kwargs)
        return response.get("items", [])

    apis = await asyncio.to_thread(_execute)
    return json.dumps({"rest_apis": apis, "count": len(apis)}, default=str)


@tool(
    name="aws_apigateway_get_resources",
    description="List resources (paths) for a REST API, including configured methods.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "rest_api_id": {
                "type": "string",
                "description": "REST API ID",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum resources to return",
            },
        },
        "required": ["rest_api_id"],
    },
    is_read_only=True,
)
async def get_resources(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "apigateway", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {"restApiId": arguments["rest_api_id"]}
        if "limit" in arguments:
            kwargs["limit"] = arguments["limit"]

        response = client.get_resources(**kwargs)
        return response.get("items", [])

    resources = await asyncio.to_thread(_execute)
    return json.dumps(
        {"resources": resources, "count": len(resources)}, default=str
    )


@tool(
    name="aws_apigateway_get_stages",
    description="List deployment stages for a REST API.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "rest_api_id": {
                "type": "string",
                "description": "REST API ID",
            },
        },
        "required": ["rest_api_id"],
    },
    is_read_only=True,
)
async def get_stages(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "apigateway", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_stages(restApiId=arguments["rest_api_id"])
        return response.get("item", [])

    stages = await asyncio.to_thread(_execute)
    return json.dumps({"stages": stages, "count": len(stages)}, default=str)


# --- HTTP / WebSocket APIs (API Gateway v2) ---


@tool(
    name="aws_apigatewayv2_get_apis",
    description="List API Gateway v2 APIs (HTTP and WebSocket).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "string",
                "description": "Maximum APIs to return (as string)",
            },
        },
    },
    is_read_only=True,
)
async def get_apis_v2(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "apigatewayv2", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_apis(**kwargs)
        return response.get("Items", [])

    apis = await asyncio.to_thread(_execute)
    return json.dumps({"apis": apis, "count": len(apis)}, default=str)


@tool(
    name="aws_apigatewayv2_get_routes",
    description="List routes for an HTTP/WebSocket API (v2).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "api_id": {
                "type": "string",
                "description": "API ID",
            },
        },
        "required": ["api_id"],
    },
    is_read_only=True,
)
async def get_routes_v2(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "apigatewayv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_routes(ApiId=arguments["api_id"])
        return response.get("Items", [])

    routes = await asyncio.to_thread(_execute)
    return json.dumps({"routes": routes, "count": len(routes)}, default=str)


@tool(
    name="aws_apigatewayv2_get_stages",
    description="List stages for an HTTP/WebSocket API (v2).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "api_id": {
                "type": "string",
                "description": "API ID",
            },
        },
        "required": ["api_id"],
    },
    is_read_only=True,
)
async def get_stages_v2(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "apigatewayv2", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_stages(ApiId=arguments["api_id"])
        return response.get("Items", [])

    stages = await asyncio.to_thread(_execute)
    return json.dumps({"stages": stages, "count": len(stages)}, default=str)
