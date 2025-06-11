#!/usr/bin/env python3
"""
MCP Orchestrator Service - Main Application
Handles Model Context Protocol (MCP) tool integration and orchestration
"""

from backend.common.service_factory import create_service_app
from backend.mcp_orchestrator.app.api.executions import router as executions_router
from backend.mcp_orchestrator.app.api.tools import router as tools_router
from backend.mcp_orchestrator.app.core.config import get_settings


async def mcp_startup_tasks():
    """MCP orchestrator specific startup tasks"""
    # TODO: Add database initialization
    # TODO: Load MCP tool configurations
    # TODO: Initialize tool execution environment
    pass


async def mcp_shutdown_tasks():
    """MCP orchestrator specific shutdown tasks"""
    # TODO: Add cleanup logic
    # TODO: Cleanup tool execution environment
    pass


# Create the service app using the DRY factory
mcp_app = create_service_app(
    service_name="MCP Orchestrator Service",
    service_description="Handles Model Context Protocol (MCP) tool integration and orchestration",
    settings_getter=get_settings,
    routers_config=[
        {"router": tools_router, "prefix": "", "tags": ["tools"]},
        {"router": executions_router, "prefix": "", "tags": ["execution"]},
    ],
    version="1.0.0",
    startup_tasks_func=mcp_startup_tasks,
    shutdown_tasks_func=mcp_shutdown_tasks,
    endpoints_config={
        "health": "/health",
        "tools": "/api/v1/tools",
        "execute": "/api/v1/executions",
    },
)

# Create the FastAPI app
app = mcp_app.create_app()

if __name__ == "__main__":
    mcp_app.run()
