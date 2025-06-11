"""
Authentication Service Configuration
Uses shared configuration system with service-specific settings
"""

from backend.common.config import AuthServiceConfig, get_auth_service_config

# Export the configuration getter for backward compatibility
get_settings = get_auth_service_config

# Export the configuration class for type hints
Settings = AuthServiceConfig


# For any service-specific configuration that might be needed
def get_auth_config() -> AuthServiceConfig:
    """Get Auth Service configuration with all settings loaded from YAML and environment"""
    return get_auth_service_config()
