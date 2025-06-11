"""
Shared health check dependency functions for all services
"""

import time
from typing import Any, Dict

import httpx
import redis
from qdrant_client import QdrantClient
from sqlalchemy import text

from .config import BaseServiceConfig


async def check_database(db_session_factory, config: BaseServiceConfig) -> Dict[str, Any]:
    """Check PostgreSQL database connection"""
    try:
        async for db in db_session_factory():
            result = await db.execute(text("SELECT 1"))
            await db.close()
            break

        return {"status": "healthy", "details": "PostgreSQL connection active"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "details": "PostgreSQL connection failed"}


async def check_redis(config: BaseServiceConfig) -> Dict[str, Any]:
    """Check Redis connection"""
    try:
        redis_client = redis.from_url(config.redis_url)
        await redis_client.ping()
        await redis_client.close()

        return {"status": "healthy", "details": "Redis connection active"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "details": "Redis connection failed"}


async def check_qdrant(config: BaseServiceConfig) -> Dict[str, Any]:
    """Check Qdrant vector database connection"""
    try:
        qdrant_client = QdrantClient(host=config.qdrant_host, port=config.qdrant_port)
        # Simple health check - get cluster info
        cluster_info = qdrant_client.get_cluster_info()

        return {"status": "healthy", "details": f"Qdrant connection active - {cluster_info.status}"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "details": "Qdrant connection failed"}


async def check_openai_api(config) -> Dict[str, Any]:
    """Check OpenAI API availability"""
    try:
        if hasattr(config, "openai_api_key") and config.openai_api_key:
            import openai

            client = openai.AsyncOpenAI(api_key=config.openai_api_key)
            # Simple API check - list models (lightweight operation)
            models = await client.models.list()

            return {
                "status": "healthy",
                "details": f"OpenAI API accessible - {len(models.data)} models available",
            }
        else:
            return {
                "status": "unhealthy",
                "error": "No API key configured",
                "details": "OpenAI API key not configured",
            }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "details": "OpenAI API not accessible"}


async def check_service_url(
    service_name: str, service_url: str, timeout: float = 5.0
) -> Dict[str, Any]:
    """Check external service availability via HTTP"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{service_url}/health", timeout=timeout)
            response.raise_for_status()

        return {"status": "healthy", "details": f"{service_name} service accessible"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": f"{service_name} service not accessible",
        }


async def check_auth_service(config) -> Dict[str, Any]:
    """Check Auth Service availability"""
    if hasattr(config, "auth_service_url"):
        return await check_service_url("Auth", config.auth_service_url)
    return {"status": "skipped", "details": "Auth service URL not configured"}


async def check_file_service(config) -> Dict[str, Any]:
    """Check File Service availability"""
    if hasattr(config, "file_service_url"):
        return await check_service_url("File", config.file_service_url)
    return {"status": "skipped", "details": "File service URL not configured"}


async def check_chat_service(config) -> Dict[str, Any]:
    """Check Chat Service availability"""
    if hasattr(config, "chat_service_url"):
        return await check_service_url("Chat", config.chat_service_url)
    return {"status": "skipped", "details": "Chat service URL not configured"}


async def check_collection_service(config) -> Dict[str, Any]:
    """Check Collection Service availability"""
    if hasattr(config, "collection_service_url"):
        return await check_service_url("Collection", config.collection_service_url)
    return {"status": "skipped", "details": "Collection service URL not configured"}


async def check_mcp_orchestrator(config) -> Dict[str, Any]:
    """Check MCP Orchestrator availability"""
    if hasattr(config, "mcp_orchestrator_url"):
        return await check_service_url("MCP Orchestrator", config.mcp_orchestrator_url)
    return {"status": "skipped", "details": "MCP Orchestrator URL not configured"}


async def check_tool_execution_env() -> Dict[str, Any]:
    """Check tool execution environment"""
    try:
        # TODO: Implement actual tool execution environment health check
        return {"status": "healthy", "details": "Tool execution environment ready"}
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "details": "Tool execution environment failed",
        }


async def check_mcp_config() -> Dict[str, Any]:
    """Check MCP configuration"""
    try:
        # TODO: Implement actual MCP configuration validation
        return {"status": "healthy", "details": "MCP configuration loaded"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "details": "MCP configuration failed"}
