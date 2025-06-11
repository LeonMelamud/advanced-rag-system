"""
Chat Service Configuration
Uses shared configuration system with service-specific settings
"""

from backend.common.config import ChatServiceConfig, get_chat_service_config

# Export the configuration getter for backward compatibility
get_settings = get_chat_service_config

# Export the configuration class for type hints
Settings = ChatServiceConfig


# For any service-specific configuration that might be needed
def get_chat_config() -> ChatServiceConfig:
    """Get Chat Service configuration with all settings loaded from YAML and environment"""
    return get_chat_service_config()
