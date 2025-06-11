#!/usr/bin/env python3
"""
File Service - Main Application
Handles file upload, processing, text extraction, chunking, and embedding generation
"""

import os

from backend.common.api import DependencyCheck, create_health_router
from backend.common.database import get_async_session
from backend.common.health_checks import check_database, check_openai_api, check_qdrant, check_redis
from backend.common.service_factory import create_service_app
from backend.file_service.app.api.files import router as files_router
from backend.file_service.app.core.config import get_settings


async def file_service_startup():
    """File service specific startup tasks"""
    # Initialize storage directory
    settings = get_settings()
    os.makedirs(settings.temp_dir, exist_ok=True)


def create_file_service_health_router():
    """Create health router with file service specific checks"""
    settings = get_settings()

    # Define dependency checks
    dependency_checks = [
        DependencyCheck("database", lambda: check_database(get_async_session, settings)),
        DependencyCheck("redis", lambda: check_redis(settings)),
        DependencyCheck("qdrant", lambda: check_qdrant(settings)),
        DependencyCheck("openai", lambda: check_openai_api(settings)),
    ]

    # Critical dependencies for readiness check
    critical_dependencies = ["database", "qdrant"]

    return create_health_router(
        service_name="File Service",
        version="1.0.0",
        dependency_checks=dependency_checks,
        critical_dependencies=critical_dependencies,
    )


# Create the service app using the DRY factory
file_app = create_service_app(
    service_name="File Service",
    service_description="Handles file upload, processing, text extraction, chunking, and embedding generation",
    settings_getter=get_settings,
    routers_config=[{"router": files_router, "prefix": "/api/v1/files", "tags": ["files"]}],
    version="1.0.0",
    startup_tasks_func=file_service_startup,
)

# Override the health router with our custom one
file_app._health_router = create_file_service_health_router()

# Create the FastAPI app
app = file_app.create_app()

# Replace the default health router with our custom one
for route in app.routes:
    if hasattr(route, "path") and route.path.startswith("/health"):
        app.routes.remove(route)

app.include_router(file_app._health_router, prefix="/health", tags=["health"])

if __name__ == "__main__":
    file_app.run()
