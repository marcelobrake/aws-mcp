"""AWS profile management tools."""
import asyncio
import json

from ..aws_client import get_profile_region, list_available_profiles
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_list_profiles",
    description=(
        "List all AWS profiles configured on this machine (from ~/.aws/config "
        "and ~/.aws/credentials). Returns profile names and their default regions."
    ),
    input_schema={
        "type": "object",
        "properties": {},
    },
    is_read_only=True,
)
async def list_profiles(arguments: dict) -> str:
    def _execute():
        profiles = list_available_profiles()
        result = []
        for name in profiles:
            region = get_profile_region(name)
            result.append({"profile": name, "region": region})
        return result

    profiles = await asyncio.to_thread(_execute)
    return json.dumps({"profiles": profiles, "count": len(profiles)}, default=str)


@tool(
    name="aws_get_caller_identity",
    description=(
        "Get the IAM identity of the current caller (STS GetCallerIdentity). "
        "Useful for verifying which AWS account and role are active for a profile."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "profile": COMMON_PROPERTIES["profile"],
            "region": COMMON_PROPERTIES["region"],
        },
    },
    is_read_only=True,
)
async def get_caller_identity(arguments: dict) -> str:
    from ..aws_client import get_client

    def _execute():
        client = get_client("sts", arguments.get("profile"), arguments.get("region"))
        response = client.get_caller_identity()
        response.pop("ResponseMetadata", None)
        return response

    result = await asyncio.to_thread(_execute)
    return json.dumps(result, default=str)
