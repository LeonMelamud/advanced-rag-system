#!/usr/bin/env python3
"""
Shared Base Main Application
DRY implementation for FastAPI service applications
"""

import logging
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from backend.common.api import create_health_router
from backend.common.utils import get_service_info, setup_logging


class BaseServiceApp(ABC):
    """
    Base class for all microservice FastAPI applications.
    Implements DRY principles for common service setup patterns.
    """

    def __init__(self, service_name: str, service_description: str, version: str = "1.0.0"):
        self.service_name = service_name
        self.service_description = service_description
        self.version = version
        self.logger = logging.getLogger(__name__)
        self.app: Optional[FastAPI] = None
        self.settings = None

    @abstractmethod
    def get_settings(self):
        """Get service-specific settings. Must be implemented by each service."""
        pass

    @abstractmethod
    def get_service_routers(self) -> List[Dict[str, Any]]:
        """
        Get service-specific routers.
        Returns list of dicts with keys: router, prefix, tags
        Example: [{"router": files_router, "prefix": "/api/v1/files", "tags": ["files"]}]
        """
        pass

    def get_service_endpoints(self) -> Dict[str, str]:
        """Get service-specific endpoints for root response. Override if needed."""
        return {"health": "/health"}

    async def startup_tasks(self):
        """Service-specific startup tasks. Override if needed."""
        self.logger.info(f"Starting {self.service_name}...")
        self.logger.info(f"{self.service_name} started successfully")

    async def shutdown_tasks(self):
        """Service-specific shutdown tasks. Override if needed."""
        self.logger.info(f"Shutting down {self.service_name}...")
        self.logger.info(f"{self.service_name} shutdown complete")

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Application lifespan manager"""
        # Startup
        await self.startup_tasks()
        yield
        # Shutdown
        await self.shutdown_tasks()

    def create_app(self) -> FastAPI:
        """Create and configure the FastAPI application"""
        # Create FastAPI application
        self.app = FastAPI(
            title=f"Advanced RAG System - {self.service_name}",
            description=self.service_description,
            version=self.version,
            lifespan=self.lifespan,
        )

        # Get settings
        self.settings = self.get_settings()

        # Setup logging
        setup_logging(self.settings.log_level)

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.settings.cors_origins,
            allow_credentials=True,
            allow_methods=self.settings.cors_methods,
            allow_headers=self.settings.cors_headers,
        )

        # Include health router
        health_router = create_health_router(service_name=self.service_name, version=self.version)
        self.app.include_router(health_router, prefix="/health", tags=["health"])

        # Include service-specific routers
        for router_config in self.get_service_routers():
            router = router_config["router"]
            config_prefix = router_config["prefix"]
            tags = router_config["tags"]

            # If router already has a prefix, don't add another one
            if hasattr(router, "prefix") and router.prefix:
                self.logger.info(f"Including router with existing prefix: {router.prefix}")
                self.app.include_router(router, tags=tags)
            else:
                self.logger.info(f"Including router with config prefix: {config_prefix}")
                self.app.include_router(router, prefix=config_prefix, tags=tags)

        # Add root endpoint
        self.app.add_api_route("/", self.root, methods=["GET"])

        # Add global exception handler
        self.app.add_exception_handler(Exception, self.global_exception_handler)

        return self.app

    async def root(self):
        """Root endpoint with service information"""
        return {
            "service": self.service_name.lower().replace(" ", "_"),
            "status": "running",
            "version": self.version,
            "description": f"Advanced RAG System - {self.service_name}",
            "endpoints": self.get_service_endpoints(),
            **get_service_info(),
        }

    async def global_exception_handler(self, request, exc):
        """Global exception handler"""
        self.logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    def run(self, host: str = None, port: int = None, reload: bool = True):
        """Run the application with uvicorn"""
        import uvicorn

        if not self.settings:
            self.settings = self.get_settings()

        uvicorn.run(
            f"{self.__module__}:app",
            host=host or self.settings.host,
            port=port or self.settings.port,
            reload=reload,
            log_level=self.settings.log_level.lower(),
        )
