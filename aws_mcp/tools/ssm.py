"""SSM (Systems Manager) tools: parameters, instances, and commands."""
import asyncio
import json

from ..aws_client import get_client
from ..config import get_config
from ..sensitive_guard import SENSITIVE_ACCESS_PROPERTIES, require_sensitive_access
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_ssm_describe_parameters",
    description="List SSM Parameter Store parameters with optional filters.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Key": {"type": "string"},
                        "Values": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "description": "Parameter filters (e.g., [{\"Key\": \"Name\", \"Values\": [\"/app/prod\"]}])",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum parameters to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_parameters(arguments: dict) -> str:
    def _execute():
        client = get_client("ssm", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "filters" in arguments:
            kwargs["ParameterFilters"] = arguments["filters"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.describe_parameters(**kwargs)
        return response.get("Parameters", [])

    params = await asyncio.to_thread(_execute)
    return json.dumps({"parameters": params, "count": len(params)}, default=str)


@tool(
    name="aws_ssm_get_parameter",
    description="Get the value of an SSM parameter. SecureString values are decrypted.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            **SENSITIVE_ACCESS_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Parameter name or ARN",
            },
            "with_decryption": {
                "type": "boolean",
                "description": "Decrypt SecureString values (default: false)",
            },
        },
        "required": ["name"],
    },
    is_read_only=True,
)
async def get_parameter(arguments: dict) -> str:
    with_decryption = arguments.get("with_decryption", False)
    if with_decryption:
        sensitive_error = require_sensitive_access(arguments, "aws_ssm_get_parameter")
        if sensitive_error:
            return json.dumps({"error": sensitive_error, "sensitive": True})

    def _execute():
        client = get_client("ssm", arguments.get("profile"), arguments.get("region"))
        response = client.get_parameter(
            Name=arguments["name"],
            WithDecryption=with_decryption,
        )
        param = response.get("Parameter", {})
        return param

    result = await asyncio.to_thread(_execute)
    return json.dumps({"parameter": result}, default=str)


@tool(
    name="aws_ssm_get_parameters_by_path",
    description="Get all SSM parameters under a path hierarchy.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            **SENSITIVE_ACCESS_PROPERTIES,
            "path": {
                "type": "string",
                "description": "Parameter path prefix (e.g., '/app/prod/')",
            },
            "recursive": {
                "type": "boolean",
                "description": "Include nested paths (default: true)",
            },
            "with_decryption": {
                "type": "boolean",
                "description": "Decrypt SecureString values (default: false)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum parameters to return",
            },
        },
        "required": ["path"],
    },
    is_read_only=True,
)
async def get_parameters_by_path(arguments: dict) -> str:
    with_decryption = arguments.get("with_decryption", False)
    if with_decryption:
        sensitive_error = require_sensitive_access(
            arguments, "aws_ssm_get_parameters_by_path"
        )
        if sensitive_error:
            return json.dumps({"error": sensitive_error, "sensitive": True})

    def _execute():
        client = get_client("ssm", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "Path": arguments["path"],
            "Recursive": arguments.get("recursive", True),
            "WithDecryption": with_decryption,
        }
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.get_parameters_by_path(**kwargs)
        return response.get("Parameters", [])

    params = await asyncio.to_thread(_execute)
    return json.dumps({"parameters": params, "count": len(params)}, default=str)


@tool(
    name="aws_ssm_describe_instance_information",
    description="List EC2 instances managed by SSM with agent status and platform info.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "filters": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Key": {"type": "string"},
                        "Values": {"type": "array", "items": {"type": "string"}},
                    },
                },
                "description": "Filters (e.g., [{\"Key\": \"PingStatus\", \"Values\": [\"Online\"]}])",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum instances to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_instance_information(arguments: dict) -> str:
    def _execute():
        client = get_client("ssm", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "filters" in arguments:
            kwargs["InstanceInformationFilterList"] = arguments["filters"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.describe_instance_information(**kwargs)
        return response.get("InstanceInformationList", [])

    instances = await asyncio.to_thread(_execute)
    return json.dumps(
        {"instances": instances, "count": len(instances)}, default=str
    )


@tool(
    name="aws_ssm_put_parameter",
    description="Create or update an SSM parameter. Blocked in --readonly mode.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "name": {
                "type": "string",
                "description": "Parameter name",
            },
            "value": {
                "type": "string",
                "description": "Parameter value",
            },
            "type": {
                "type": "string",
                "enum": ["String", "StringList", "SecureString"],
                "description": "Parameter type (default: String)",
            },
            "overwrite": {
                "type": "boolean",
                "description": "Overwrite existing parameter (default: false)",
            },
            "description": {
                "type": "string",
                "description": "Parameter description",
            },
        },
        "required": ["name", "value"],
    },
    is_read_only=False,
)
async def put_parameter(arguments: dict) -> str:
    config = get_config()
    if config.readonly:
        return json.dumps({
            "error": "BLOCKED by readonly mode: SSM PutParameter is not allowed. Remove --readonly to enable.",
            "readonly": True,
        })

    def _execute():
        client = get_client("ssm", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "Name": arguments["name"],
            "Value": arguments["value"],
            "Type": arguments.get("type", "String"),
            "Overwrite": arguments.get("overwrite", False),
        }
        if "description" in arguments:
            kwargs["Description"] = arguments["description"]

        response = client.put_parameter(**kwargs)
        return {"Version": response.get("Version")}

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
