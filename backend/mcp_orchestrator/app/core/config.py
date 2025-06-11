"""
MCP Orchestrator Service Configuration
Uses shared configuration system with service-specific settings
"""

from backend.common.config import MCPOrchestratorConfig, get_mcp_orchestrator_config

# Export the configuration getter for backward compatibility
get_settings = get_mcp_orchestrator_config

# Export the configuration class for type hints
Settings = MCPOrchestratorConfig


# For any service-specific configuration that might be needed
def get_mcp_config() -> MCPOrchestratorConfig:
    """Get MCP Orchestrator configuration with all settings loaded from YAML and environment"""
    return get_mcp_orchestrator_config()
