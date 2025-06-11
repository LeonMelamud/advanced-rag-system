#!/usr/bin/env python3
"""
Chat Service - Main Application
Handles chat sessions, conversation history, and RAG orchestration
"""

from backend.chat_service.app.api.chat import router as chat_router
from backend.chat_service.app.api.sessions import router as sessions_router
from backend.chat_service.app.core.config import get_settings
from backend.common.service_factory import create_service_app

# Create the service app using the DRY factory
chat_app = create_service_app(
    service_name="Chat Service",
    service_description="Handles chat sessions, conversation history, and RAG orchestration",
    settings_getter=get_settings,
    routers_config=[
        {"router": chat_router, "prefix": "/api/v1/chat", "tags": ["chat"]},
        {"router": sessions_router, "prefix": "/api/v1/sessions", "tags": ["sessions"]},
    ],
    version="1.0.0",
    endpoints_config={"health": "/health", "chat": "/api/v1/chat", "sessions": "/api/v1/sessions"},
)

# Create the FastAPI app
app = chat_app.create_app()

if __name__ == "__main__":
    chat_app.run()
