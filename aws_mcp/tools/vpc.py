"""VPC tools: VPCs, subnets, gateways, and route tables."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_vpc_describe_vpcs",
    description="Describe VPCs in the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "vpc_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific VPC IDs to describe (optional — returns all if omitted)",
            },
        },
    },
    is_read_only=True,
)
async def describe_vpcs(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "vpc_ids" in arguments:
            kwargs["VpcIds"] = arguments["vpc_ids"]
        response = client.describe_vpcs(**kwargs)
        return response.get("Vpcs", [])

    vpcs = await asyncio.to_thread(_execute)
    return json.dumps({"vpcs": vpcs, "count": len(vpcs)}, default=str)


@tool(
    name="aws_vpc_describe_subnets",
    description="Describe subnets, optionally filtered by VPC.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "vpc_id": {
                "type": "string",
                "description": "Filter subnets by VPC ID",
            },
            "subnet_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific subnet IDs to describe",
            },
        },
    },
    is_read_only=True,
)
async def describe_subnets(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "vpc_id" in arguments:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [arguments["vpc_id"]]}]
        if "subnet_ids" in arguments:
            kwargs["SubnetIds"] = arguments["subnet_ids"]
        response = client.describe_subnets(**kwargs)
        return response.get("Subnets", [])

    subnets = await asyncio.to_thread(_execute)
    return json.dumps({"subnets": subnets, "count": len(subnets)}, default=str)


@tool(
    name="aws_vpc_describe_nat_gateways",
    description="Describe NAT gateways, optionally filtered by VPC.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "vpc_id": {
                "type": "string",
                "description": "Filter by VPC ID",
            },
        },
    },
    is_read_only=True,
)
async def describe_nat_gateways(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "vpc_id" in arguments:
            kwargs["Filter"] = [{"Name": "vpc-id", "Values": [arguments["vpc_id"]]}]
        response = client.describe_nat_gateways(**kwargs)
        return response.get("NatGateways", [])

    gateways = await asyncio.to_thread(_execute)
    return json.dumps({"nat_gateways": gateways, "count": len(gateways)}, default=str)


@tool(
    name="aws_vpc_describe_internet_gateways",
    description="Describe internet gateways, optionally filtered by attached VPC.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "vpc_id": {
                "type": "string",
                "description": "Filter by attached VPC ID",
            },
        },
    },
    is_read_only=True,
)
async def describe_internet_gateways(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "vpc_id" in arguments:
            kwargs["Filters"] = [{"Name": "attachment.vpc-id", "Values": [arguments["vpc_id"]]}]
        response = client.describe_internet_gateways(**kwargs)
        return response.get("InternetGateways", [])

    igws = await asyncio.to_thread(_execute)
    return json.dumps({"internet_gateways": igws, "count": len(igws)}, default=str)


@tool(
    name="aws_vpc_describe_route_tables",
    description="Describe route tables, optionally filtered by VPC.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "vpc_id": {
                "type": "string",
                "description": "Filter by VPC ID",
            },
        },
    },
    is_read_only=True,
)
async def describe_route_tables(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "vpc_id" in arguments:
            kwargs["Filters"] = [{"Name": "vpc-id", "Values": [arguments["vpc_id"]]}]
        response = client.describe_route_tables(**kwargs)
        return response.get("RouteTables", [])

    tables = await asyncio.to_thread(_execute)
    return json.dumps({"route_tables": tables, "count": len(tables)}, default=str)


@tool(
    name="aws_vpc_describe_vpc_peering_connections",
    description="Describe VPC peering connections in the account.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
        },
    },
    is_read_only=True,
)
async def describe_vpc_peering_connections(arguments: dict) -> str:
    def _execute():
        client = get_client("ec2", arguments.get("profile"), arguments.get("region"))
        response = client.describe_vpc_peering_connections()
        return response.get("VpcPeeringConnections", [])

    connections = await asyncio.to_thread(_execute)
    return json.dumps(
        {"peering_connections": connections, "count": len(connections)}, default=str
    )
