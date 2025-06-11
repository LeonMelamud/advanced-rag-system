"""
Collection Service Configuration
Uses shared configuration system with service-specific settings
"""

from backend.common.config import CollectionServiceConfig, get_collection_service_config

# Export the configuration getter for backward compatibility
get_settings = get_collection_service_config

# Export the configuration class for type hints
Settings = CollectionServiceConfig


# For any service-specific configuration that might be needed
def get_collection_config() -> CollectionServiceConfig:
    """Get Collection Service configuration with all settings loaded from YAML and environment"""
    return get_collection_service_config()
