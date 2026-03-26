"""Step Functions tools: state machines and executions."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_sfn_list_state_machines",
    description="List Step Functions state machines.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum state machines to return",
            },
        },
    },
    is_read_only=True,
)
async def list_state_machines(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "stepfunctions", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]
        response = client.list_state_machines(**kwargs)
        return response.get("stateMachines", [])

    machines = await asyncio.to_thread(_execute)
    return json.dumps({"state_machines": machines, "count": len(machines)}, default=str)


@tool(
    name="aws_sfn_describe_state_machine",
    description="Get the full definition and configuration of a Step Functions state machine.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "state_machine_arn": {
                "type": "string",
                "description": "State machine ARN",
            },
        },
        "required": ["state_machine_arn"],
    },
    is_read_only=True,
)
async def describe_state_machine(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "stepfunctions", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_state_machine(
            stateMachineArn=arguments["state_machine_arn"]
        )
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps({"state_machine": result}, default=str)


@tool(
    name="aws_sfn_list_executions",
    description="List executions for a Step Functions state machine.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "state_machine_arn": {
                "type": "string",
                "description": "State machine ARN",
            },
            "status_filter": {
                "type": "string",
                "enum": ["RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "ABORTED"],
                "description": "Filter by execution status",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum executions to return (default: 20)",
            },
        },
        "required": ["state_machine_arn"],
    },
    is_read_only=True,
)
async def list_executions(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "stepfunctions", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "stateMachineArn": arguments["state_machine_arn"],
            "maxResults": arguments.get("max_results", 20),
        }
        if "status_filter" in arguments:
            kwargs["statusFilter"] = arguments["status_filter"]
        response = client.list_executions(**kwargs)
        return response.get("executions", [])

    executions = await asyncio.to_thread(_execute)
    return json.dumps({"executions": executions, "count": len(executions)}, default=str)


@tool(
    name="aws_sfn_describe_execution",
    description="Get the status, input, and output of a specific Step Functions execution.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "execution_arn": {
                "type": "string",
                "description": "Execution ARN",
            },
        },
        "required": ["execution_arn"],
    },
    is_read_only=True,
)
async def describe_execution(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "stepfunctions", arguments.get("profile"), arguments.get("region")
        )
        response = client.describe_execution(
            executionArn=arguments["execution_arn"]
        )
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps({"execution": result}, default=str)


@tool(
    name="aws_sfn_get_execution_history",
    description="Get the event history of a Step Functions execution (steps, errors, inputs/outputs).",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "execution_arn": {
                "type": "string",
                "description": "Execution ARN",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum events to return (default: 50)",
            },
            "reverse_order": {
                "type": "boolean",
                "description": "Return events in reverse chronological order (default: false)",
            },
        },
        "required": ["execution_arn"],
    },
    is_read_only=True,
)
async def get_execution_history(arguments: dict) -> str:
    def _execute():
        client = get_client(
            "stepfunctions", arguments.get("profile"), arguments.get("region")
        )
        kwargs: dict = {
            "executionArn": arguments["execution_arn"],
            "maxResults": arguments.get("max_results", 50),
            "reverseOrder": arguments.get("reverse_order", False),
        }
        response = client.get_execution_history(**kwargs)
        return response.get("events", [])

    events = await asyncio.to_thread(_execute)
    return json.dumps({"events": events, "count": len(events)}, default=str)
