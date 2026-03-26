"""AWS Backup tools: backup plans, jobs, and recovery points."""
import asyncio
import json

from ..aws_client import get_client
from . import COMMON_PROPERTIES, tool


@tool(
    name="aws_backup_list_backup_plans",
    description="List AWS Backup plans.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "include_deleted": {
                "type": "boolean",
                "description": "Include deleted backup plans (default: false)",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum plans to return",
            },
        },
    },
    is_read_only=True,
)
async def list_backup_plans(arguments: dict) -> str:
    def _execute():
        client = get_client("backup", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "IncludeDeleted": arguments.get("include_deleted", False),
        }
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        response = client.list_backup_plans(**kwargs)
        return response.get("BackupPlansList", [])

    plans = await asyncio.to_thread(_execute)
    return json.dumps({"backup_plans": plans, "count": len(plans)}, default=str)


@tool(
    name="aws_backup_list_backup_jobs",
    description="List AWS Backup jobs with their status and resource details.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "by_state": {
                "type": "string",
                "enum": ["CREATED", "PENDING", "RUNNING", "ABORTING", "ABORTED",
                         "COMPLETED", "FAILED", "EXPIRED", "PARTIAL"],
                "description": "Filter by job state",
            },
            "by_resource_type": {
                "type": "string",
                "description": "Filter by resource type (e.g., 'EC2', 'RDS', 'DynamoDB', 'EFS', 'S3')",
            },
            "by_backup_vault_name": {
                "type": "string",
                "description": "Filter by backup vault name",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum jobs to return (default: 50)",
            },
        },
    },
    is_read_only=True,
)
async def list_backup_jobs(arguments: dict) -> str:
    def _execute():
        client = get_client("backup", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "MaxResults": arguments.get("max_results", 50),
        }
        if "by_state" in arguments:
            kwargs["ByState"] = arguments["by_state"]
        if "by_resource_type" in arguments:
            kwargs["ByResourceType"] = arguments["by_resource_type"]
        if "by_backup_vault_name" in arguments:
            kwargs["ByBackupVaultName"] = arguments["by_backup_vault_name"]
        response = client.list_backup_jobs(**kwargs)
        return response.get("BackupJobs", [])

    jobs = await asyncio.to_thread(_execute)
    return json.dumps({"backup_jobs": jobs, "count": len(jobs)}, default=str)


@tool(
    name="aws_backup_list_backup_vaults",
    description="List AWS Backup vaults.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "max_results": {
                "type": "integer",
                "description": "Maximum vaults to return",
            },
        },
    },
    is_read_only=True,
)
async def list_backup_vaults(arguments: dict) -> str:
    def _execute():
        client = get_client("backup", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {}
        if "max_results" in arguments:
            kwargs["MaxResults"] = arguments["max_results"]
        response = client.list_backup_vaults(**kwargs)
        return response.get("BackupVaultList", [])

    vaults = await asyncio.to_thread(_execute)
    return json.dumps({"backup_vaults": vaults, "count": len(vaults)}, default=str)


@tool(
    name="aws_backup_list_recovery_points_by_backup_vault",
    description="List recovery points (backups) stored in a backup vault.",
    input_schema={
        "type": "object",
        "properties": {
            **COMMON_PROPERTIES,
            "backup_vault_name": {
                "type": "string",
                "description": "Backup vault name",
            },
            "by_resource_type": {
                "type": "string",
                "description": "Filter by resource type (e.g., 'EC2', 'RDS', 'EFS')",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum recovery points to return (default: 50)",
            },
        },
        "required": ["backup_vault_name"],
    },
    is_read_only=True,
)
async def list_recovery_points_by_backup_vault(arguments: dict) -> str:
    def _execute():
        client = get_client("backup", arguments.get("profile"), arguments.get("region"))
        kwargs: dict = {
            "BackupVaultName": arguments["backup_vault_name"],
            "MaxResults": arguments.get("max_results", 50),
        }
        if "by_resource_type" in arguments:
            kwargs["ByResourceType"] = arguments["by_resource_type"]
        response = client.list_recovery_points_by_backup_vault(**kwargs)
        return response.get("RecoveryPoints", [])

    points = await asyncio.to_thread(_execute)
    return json.dumps({"recovery_points": points, "count": len(points)}, default=str)
