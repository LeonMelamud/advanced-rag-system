#!/usr/bin/env python3
"""
Authentication Service - Main Application
Handles user authentication, authorization, and JWT token management
"""

from backend.auth_service.app.api.auth import router as auth_router
from backend.auth_service.app.core.config import get_settings
from backend.common.service_factory import create_service_app

# Create the service app using the DRY factory
auth_app = create_service_app(
    service_name="Authentication Service",
    service_description="Handles user authentication, authorization, and JWT token management",
    settings_getter=get_settings,
    routers_config=[{"router": auth_router, "prefix": "/api/v1/auth", "tags": ["authentication"]}],
    version="1.0.0",
)

# Create the FastAPI app
app = auth_app.create_app()

if __name__ == "__main__":
    auth_app.run()
