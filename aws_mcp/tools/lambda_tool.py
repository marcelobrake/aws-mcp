"""Lambda tools: function listing, details, and invocation."""
import asyncio
import base64
import json
import logging

from ..aws_client import get_client
from ..config import get_config
from . import COMMON_PROPERTIES, tool

logger = logging.getLogger("aws_mcp")


@tool(
    name="aws_lambda_list_functions",
    description="List Lambda functions in the account/region.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_items": {
                "type": "integer",
                "description": "Maximum number of functions to return",
            },
        },
    },
    is_read_only=True,
)
async def list_functions(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "lambda", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_items" in arguments:
            kwargs["MaxItems"] = arguments["max_items"]

        response = client.list_functions(**kwargs)
        functions = [
            {
                "FunctionName": f["FunctionName"],
                "Runtime": f.get("Runtime"),
                "Handler": f.get("Handler"),
                "CodeSize": f.get("CodeSize"),
                "Description": f.get("Description"),
                "LastModified": f.get("LastModified"),
                "MemorySize": f.get("MemorySize"),
                "Timeout": f.get("Timeout"),
                "FunctionArn": f.get("FunctionArn"),
            }
            for f in response.get("Functions", [])
        ]
        return functions

    functions = await asyncio.to_thread(_execute)
    return json.dumps(
        {"functions": functions, "count": len(functions)}, default=str
    )


@tool(
    name="aws_lambda_get_function",
    description="Get detailed configuration and metadata for a Lambda function.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "function_name": {
                "type": "string",
                "description": "Function name or ARN",
            },
        },
        "required": ["function_name"],
    },
    is_read_only=True,
)
async def get_function(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "lambda", arguments.get("profile"), arguments.get("region")
        )
        response = client.get_function(
            FunctionName=arguments["function_name"]
        )
        response.pop("ResponseMetadata", None)
        # Remove Code.Location for security (pre-signed URL)
        if "Code" in response:
            response["Code"].pop("Location", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)


@tool(
    name="aws_lambda_invoke",
    description=(
        "Invoke a Lambda function. In --readonly mode, uses InvocationType='DryRun' "
        "to validate permissions without executing the function."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "function_name": {
                "type": "string",
                "description": "Function name or ARN",
            },
            "payload": {
                "type": "object",
                "description": "JSON payload to send to the function",
            },
            "invocation_type": {
                "type": "string",
                "enum": ["RequestResponse", "Event"],
                "description": "Invocation type: 'RequestResponse' (sync) or 'Event' (async). Default: RequestResponse",
            },
        },
        "required": ["function_name"],
    },
    is_read_only=False,
)
async def invoke_function(arguments: dict) -> str:
    config = get_config()

    def _execute():
        client = get_client(
            "lambda", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "FunctionName": arguments["function_name"],
        }

        if config.readonly:
            kwargs["InvocationType"] = "DryRun"
        else:
            kwargs["InvocationType"] = arguments.get(
                "invocation_type", "RequestResponse"
            )

        if "payload" in arguments:
            kwargs["Payload"] = json.dumps(arguments["payload"]).encode("utf-8")

        response = client.invoke(**kwargs)
        result: dict = {
            "StatusCode": response.get("StatusCode"),
            "FunctionError": response.get("FunctionError"),
            "ExecutedVersion": response.get("ExecutedVersion"),
        }

        if config.readonly:
            result["dry_run"] = True
            result["message"] = (
                f"DryRun succeeded: invocation of '{arguments['function_name']}' would be allowed"
            )
        else:
            payload_stream = response.get("Payload")
            if payload_stream:
                payload_bytes = payload_stream.read()
                try:
                    result["payload"] = json.loads(payload_bytes)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    result["payload"] = base64.b64encode(payload_bytes).decode("ascii")

        return result

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
