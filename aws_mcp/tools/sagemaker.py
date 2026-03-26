"""SageMaker tools: endpoints, notebooks, and training jobs."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_sagemaker_list_endpoints",
    description="List SageMaker inference endpoints.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "status_equals": {
                "type": "string",
                "enum": [
                    "InService",
                    "Creating",
                    "Updating",
                    "SystemUpdating",
                    "RollingBack",
                    "Deleting",
                    "Failed",
                ],
                "description": "Filter by status",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum endpoints to return",
            },
        },
    },
    is_read_only=True,
)
async def list_endpoints(arguments: dict) -> str:
    def _execute():
        client = get_client("sagemaker", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "status_equals" in arguments:
            kwargs["StatusEquals"] = arguments["status_equals"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_endpoints(**kwargs)
        return response["Endpoints"]

    endpoints = await asyncio.to_thread(_execute)
    return json.dumps({"endpoints": endpoints, "count": len(endpoints)}, default=str)


@tool(
    name="aws_sagemaker_describe_endpoint",
    description="Describe a SageMaker endpoint.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "endpoint_name": {
                "type": "string",
                "description": "Endpoint name",
            },
        },
        "required": ["endpoint_name"],
    },
    is_read_only=True,
)
async def describe_endpoint(arguments: dict) -> str:
    def _execute():
        client = get_client("sagemaker", arguments.get("profile"), arguments.get("region"))
        result = client.describe_endpoint(EndpointName=arguments["endpoint_name"])
        result.pop("ResponseMetadata", None)
        return result

    result = await asyncio.to_thread(_execute)
    return json.dumps({"endpoint": result}, default=str)


@tool(
    name="aws_sagemaker_list_notebook_instances",
    description="List SageMaker notebook instances.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "status_equals": {
                "type": "string",
                "enum": [
                    "InService",
                    "Stopped",
                    "Pending",
                    "Stopping",
                    "Updating",
                    "Deleting",
                    "Failed",
                ],
                "description": "Filter by status",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum instances to return",
            },
        },
    },
    is_read_only=True,
)
async def list_notebook_instances(arguments: dict) -> str:
    def _execute():
        client = get_client("sagemaker", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "status_equals" in arguments:
            kwargs["StatusEquals"] = arguments["status_equals"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_notebook_instances(**kwargs)
        return response["NotebookInstances"]

    notebook_instances = await asyncio.to_thread(_execute)
    return json.dumps(
        {"notebook_instances": notebook_instances, "count": len(notebook_instances)},
        default=str,
    )


@tool(
    name="aws_sagemaker_list_training_jobs",
    description="List SageMaker training jobs.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "status_equals": {
                "type": "string",
                "enum": [
                    "InProgress",
                    "Completed",
                    "Failed",
                    "Stopping",
                    "Stopped",
                ],
                "description": "Filter by status",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum jobs to return",
            },
        },
    },
    is_read_only=True,
)
async def list_training_jobs(arguments: dict) -> str:
    def _execute():
        client = get_client("sagemaker", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "status_equals" in arguments:
            kwargs["StatusEquals"] = arguments["status_equals"]
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]

        response = client.list_training_jobs(**kwargs)
        return response["TrainingJobSummaries"]

    training_jobs = await asyncio.to_thread(_execute)
    return json.dumps(
        {"training_jobs": training_jobs, "count": len(training_jobs)}, default=str
    )
