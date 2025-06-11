#!/usr/bin/env python3
"""
Collection Service - Main Application
Handles Knowledge Collection management, configuration, and versioning
"""

from backend.collection_service.app.api.collections import router as collections_router
from backend.collection_service.app.api.versions import router as versions_router
from backend.collection_service.app.core.config import get_settings
from backend.common.service_factory import create_service_app

# Create the service app using the DRY factory
collection_app = create_service_app(
    service_name="Collection Service",
    service_description="Handles Knowledge Collection management, configuration, and versioning",
    settings_getter=get_settings,
    routers_config=[
        {"router": collections_router, "prefix": "/api/v1/collections", "tags": ["collections"]},
        {"router": versions_router, "prefix": "/api/v1/versions", "tags": ["versions"]},
    ],
    version="1.0.0",
    endpoints_config={
        "health": "/health",
        "collections": "/api/v1/collections",
        "versions": "/api/v1/versions",
    },
)

# Create the FastAPI app
app = collection_app.create_app()

if __name__ == "__main__":
    collection_app.run()
