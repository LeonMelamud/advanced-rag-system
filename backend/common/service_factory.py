#!/usr/bin/env python3
"""
Service Factory - DRY Implementation
Creates service applications without code duplication
"""

from typing import Any, Callable, Dict, List

from backend.common.main_base import BaseServiceApp


class ServiceApp(BaseServiceApp):
    """
    Generic service application that can be configured for any service.
    Eliminates the need for service-specific app classes.
    """

    def __init__(
        self,
        service_name: str,
        service_description: str,
        version: str,
        settings_getter: Callable,
        routers_config: List[Dict[str, Any]],
        startup_tasks_func: Callable = None,
        shutdown_tasks_func: Callable = None,
        endpoints_config: Dict[str, str] = None,
    ):
        super().__init__(service_name, service_description, version)
        self._settings_getter = settings_getter
        self._routers_config = routers_config
        self._startup_tasks_func = startup_tasks_func
        self._shutdown_tasks_func = shutdown_tasks_func
        self._endpoints_config = endpoints_config or {"health": "/health"}

    def get_settings(self):
        """Get service settings using the provided getter function"""
        return self._settings_getter()

    def get_service_routers(self) -> List[Dict[str, Any]]:
        """Get service routers from configuration"""
        return self._routers_config

    def get_service_endpoints(self) -> Dict[str, str]:
        """Get service endpoints from configuration"""
        return self._endpoints_config

    async def startup_tasks(self):
        """Execute custom startup tasks if provided"""
        await super().startup_tasks()
        if self._startup_tasks_func:
            await self._startup_tasks_func()

    async def shutdown_tasks(self):
        """Execute custom shutdown tasks if provided"""
        if self._shutdown_tasks_func:
            await self._shutdown_tasks_func()
        await super().shutdown_tasks()


def create_service_app(
    service_name: str,
    service_description: str,
    settings_getter: Callable,
    routers_config: List[Dict[str, Any]],
    version: str = "1.0.0",
    startup_tasks_func: Callable = None,
    shutdown_tasks_func: Callable = None,
    endpoints_config: Dict[str, str] = None,
) -> ServiceApp:
    """
    Factory function to create a service application.

    Args:
        service_name: Name of the service
        service_description: Description of the service
        settings_getter: Function that returns service settings
        routers_config: List of router configurations
        version: Service version
        startup_tasks_func: Optional custom startup tasks function
        shutdown_tasks_func: Optional custom shutdown tasks function
        endpoints_config: Optional custom endpoints configuration

    Returns:
        Configured ServiceApp instance
    """
    return ServiceApp(
        service_name=service_name,
        service_description=service_description,
        version=version,
        settings_getter=settings_getter,
        routers_config=routers_config,
        startup_tasks_func=startup_tasks_func,
        shutdown_tasks_func=shutdown_tasks_func,
        endpoints_config=endpoints_config,
    )
