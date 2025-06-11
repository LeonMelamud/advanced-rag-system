"""
Auth Service Health Check Endpoints - Using Shared Health System
"""

from fastapi import APIRouter

from backend.common.api import DependencyCheck, create_health_router
from backend.common.database import get_db
from backend.common.health_checks import check_database, check_redis

from ..core.config import get_settings


# Create dependency checks for auth service
def create_auth_health_router() -> APIRouter:
    """Create health router with auth service specific dependencies"""
    settings = get_settings()

    dependency_checks = [
        DependencyCheck("database", lambda: check_database(get_db, settings)),
        DependencyCheck("redis", lambda: check_redis(settings)),
    ]

    critical_dependencies = ["database", "redis"]

    return create_health_router(
        service_name="auth_service",
        version="1.0.0",
        dependency_checks=dependency_checks,
        critical_dependencies=critical_dependencies,
    )


# Create the router
router = create_auth_health_router()
