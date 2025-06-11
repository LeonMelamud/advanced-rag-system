"""
File Service Configuration
Uses shared configuration system with service-specific settings
"""

from backend.common.config import FileServiceConfig, get_file_service_config

# Export the configuration getter for backward compatibility
get_settings = get_file_service_config

# Export the configuration class for type hints
Settings = FileServiceConfig


# For any service-specific configuration that might be needed
def get_file_config() -> FileServiceConfig:
    """Get File Service configuration with all settings loaded from YAML and environment"""
    return get_file_service_config()
