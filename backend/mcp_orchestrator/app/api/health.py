"""
MCP Orchestrator Service Health Check Endpoints - Using Shared Health System
"""

from fastapi import APIRouter

from backend.common.api import DependencyCheck, create_health_router
from backend.common.database import get_db
from backend.common.health_checks import (
    check_database,
    check_mcp_config,
    check_redis,
    check_tool_execution_env,
)

from ..core.config import get_settings


# Create dependency checks for MCP orchestrator service
def create_mcp_health_router() -> APIRouter:
    """Create health router with MCP orchestrator specific dependencies"""
    settings = get_settings()

    dependency_checks = [
        DependencyCheck("database", lambda: check_database(get_db, settings)),
        DependencyCheck("redis", lambda: check_redis(settings)),
        DependencyCheck("execution_env", lambda: check_tool_execution_env()),
        DependencyCheck("mcp_config", lambda: check_mcp_config()),
    ]

    critical_dependencies = ["database"]

    return create_health_router(
        service_name="mcp_orchestrator",
        version="1.0.0",
        dependency_checks=dependency_checks,
        critical_dependencies=critical_dependencies,
    )


# Create the router
router = create_mcp_health_router()
