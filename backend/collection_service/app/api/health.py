"""
Collection Service Health Check Endpoints - Using Shared Health System
"""

from fastapi import APIRouter

from backend.common.api import DependencyCheck, create_health_router
from backend.common.database import get_db
from backend.common.health_checks import (
    check_auth_service,
    check_database,
    check_file_service,
    check_qdrant,
    check_redis,
)

from ..core.config import get_settings


# Create dependency checks for collection service
def create_collection_health_router() -> APIRouter:
    """Create health router with collection service specific dependencies"""
    settings = get_settings()

    dependency_checks = [
        DependencyCheck("database", lambda: check_database(get_db, settings)),
        DependencyCheck("redis", lambda: check_redis(settings)),
        DependencyCheck("vector_db", lambda: check_qdrant(settings)),
        DependencyCheck("auth_service", lambda: check_auth_service(settings)),
        DependencyCheck("file_service", lambda: check_file_service(settings)),
    ]

    critical_dependencies = ["database", "redis"]

    return create_health_router(
        service_name="collection_service",
        version="1.0.0",
        dependency_checks=dependency_checks,
        critical_dependencies=critical_dependencies,
    )


# Create the router
router = create_collection_health_router()
