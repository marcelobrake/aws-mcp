"""AWS client and session management.

Provides helpers to create boto3 sessions and service clients,
and to list the AWS profiles configured on the machine.
"""
import configparser
import logging
from pathlib import Path
from typing import Any

import boto3
import botocore.session

logger = logging.getLogger("aws_mcp")


def list_available_profiles() -> list[str]:
    """Return all AWS profile names from ~/.aws/config and ~/.aws/credentials."""
    try:
        session = botocore.session.Session()
        profiles = list(session.available_profiles)
        logger.debug(
            f"Found {len(profiles)} AWS profiles",
            extra={"tool_name": "aws_client"},
        )
        return profiles
    except Exception:
        logger.warning(
            "Failed to list profiles via botocore, falling back to config file parsing",
            extra={"tool_name": "aws_client"},
        )
        return _parse_profiles_from_config()


def _parse_profiles_from_config() -> list[str]:
    """Fallback: parse profile names directly from ~/.aws/config."""
    config_path = Path.home() / ".aws" / "config"
    if not config_path.exists():
        return []

    config = configparser.ConfigParser()
    config.read(str(config_path))

    profiles: list[str] = []
    for section in config.sections():
        if section == "default":
            profiles.append("default")
        elif section.startswith("profile "):
            profiles.append(section[len("profile ") :])
    return profiles


def get_profile_region(profile: str) -> str | None:
    """Return the default region for a given profile, or None."""
    try:
        session = boto3.Session(profile_name=profile)
        return session.region_name
    except Exception:
        return None


def create_session(
    profile: str | None = None, region: str | None = None
) -> boto3.Session:
    """Create a boto3 session with optional profile and region override."""
    kwargs: dict[str, str] = {}
    if profile:
        kwargs["profile_name"] = profile
    if region:
        kwargs["region_name"] = region

    session = boto3.Session(**kwargs)
    logger.debug(
        f"Created boto3 session: profile={session.profile_name}, region={session.region_name}",
        extra={
            "tool_name": "aws_client",
            "aws_profile": session.profile_name,
            "aws_region": session.region_name,
        },
    )
    return session


def get_client(
    service: str,
    profile: str | None = None,
    region: str | None = None,
) -> Any:
    """Create a boto3 service client."""
    session = create_session(profile, region)
    return session.client(service)


def get_resource(
    service: str,
    profile: str | None = None,
    region: str | None = None,
) -> Any:
    """Create a boto3 service resource."""
    session = create_session(profile, region)
    return session.resource(service)
