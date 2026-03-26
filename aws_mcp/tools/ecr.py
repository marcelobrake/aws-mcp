"""ECR tools: repositories and images."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_ecr_describe_repositories",
    description="List and describe ECR repositories.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "repository_names": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by repository names (optional)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum repositories to return",
            },
        },
    },
    is_read_only=True,
)
async def describe_repositories(arguments: dict) -> str:
    def _execute():
        client = get_client("ecr", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "repository_names" in arguments:
            kwargs["repositoryNames"] = arguments["repository_names"]
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]

        response = client.describe_repositories(**kwargs)
        repos = response.get("repositories", [])
        return repos

    repos = await asyncio.to_thread(_execute)
    return json.dumps({"repositories": repos, "count": len(repos)}, default=str)


@tool(
    name="aws_ecr_list_images",
    description="List images in an ECR repository with tag status and digest.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "repository_name": {
                "type": "string",
                "description": "ECR repository name",
            },
            "tag_status": {
                "type": "string",
                "enum": ["TAGGED", "UNTAGGED", "ANY"],
                "description": "Filter by tag status (default: ANY)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum images to return",
            },
        },
        "required": ["repository_name"],
    },
    is_read_only=True,
)
async def list_images(arguments: dict) -> str:
    def _execute():
        client = get_client("ecr", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"repositoryName": arguments["repository_name"]}
        if "tag_status" in arguments:
            kwargs["filter"] = {"tagStatus": arguments["tag_status"]}
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]

        response = client.list_images(**kwargs)
        return response.get("imageIds", [])

    images = await asyncio.to_thread(_execute)
    return json.dumps({"image_ids": images, "count": len(images)}, default=str)


@tool(
    name="aws_ecr_describe_images",
    description=(
        "Get detailed metadata for ECR images: size, push date, scan status, "
        "and vulnerability counts."
    ),
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "repository_name": {
                "type": "string",
                "description": "ECR repository name",
            },
            "image_ids": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "imageTag": {"type": "string"},
                        "imageDigest": {"type": "string"},
                    },
                },
                "description": "Image tags or digests to describe (e.g., [{\"imageTag\": \"latest\"}])",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum images to return",
            },
        },
        "required": ["repository_name"],
    },
    is_read_only=True,
)
async def describe_images(arguments: dict) -> str:
    def _execute():
        client = get_client("ecr", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {"repositoryName": arguments["repository_name"]}
        if "image_ids" in arguments:
            kwargs["imageIds"] = arguments["image_ids"]
        if "max_results" in arguments:
            kwargs["maxResults"] = arguments["max_results"]

        response = client.describe_images(**kwargs)
        return response.get("imageDetails", [])

    images = await asyncio.to_thread(_execute)
    return json.dumps({"image_details": images, "count": len(images)}, default=str)


@tool(
    name="aws_ecr_get_lifecycle_policy",
    description="Get the lifecycle policy for an ECR repository.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "repository_name": {
                "type": "string",
                "description": "ECR repository name",
            },
        },
        "required": ["repository_name"],
    },
    is_read_only=True,
)
async def get_lifecycle_policy(arguments: dict) -> str:
    def _execute():
        client = get_client("ecr", arguments.get("profile"), arguments.get("region"))
        try:
            response = client.get_lifecycle_policy(
                repositoryName=arguments["repository_name"]
            )
            policy_text = response.get("lifecyclePolicyText", "{}")
            return {
                "repository_name": response.get("repositoryName"),
                "policy": json.loads(policy_text),
            }
        except client.exceptions.LifecyclePolicyNotFoundException:
            return {
                "repository_name": arguments["repository_name"],
                "policy": None,
                "message": "No lifecycle policy configured",
            }

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
