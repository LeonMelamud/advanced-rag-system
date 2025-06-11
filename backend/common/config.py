"""
Shared Configuration System with Environment Integration
Centralized configuration loading from config/environments/ directory
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field, validator
from pydantic_settings import BaseSettings


def load_yaml_config(environment: str = None) -> Dict[str, Any]:
    """Load configuration from YAML files"""
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")

    # Get project root (assuming we're in backend/common/)
    project_root = Path(__file__).parent.parent.parent
    config_dir = project_root / "config" / "environments"

    # Load default config first
    default_config_path = project_root / "config" / "default.yaml"
    config = {}

    if default_config_path.exists():
        with open(default_config_path, "r") as f:
            config = yaml.safe_load(f) or {}

    # Load environment-specific config
    env_config_path = config_dir / f"{environment}.yaml"
    if env_config_path.exists():
        with open(env_config_path, "r") as f:
            env_config = yaml.safe_load(f) or {}
            # Deep merge environment config over default
            config = deep_merge(config, env_config)

    return config


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class BaseServiceConfig(BaseSettings):
    """Base configuration for all services with YAML integration"""

    # Service Identity
    service_name: str = "unknown_service"
    version: str = "1.0.0"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # Redis Configuration
    redis_url: str = Field(..., env="REDIS_URL")
    redis_db: int = 0
    redis_decode_responses: bool = True

    # JWT Configuration
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    cors_credentials: bool = True

    # Security Configuration
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # Rate Limiting
    rate_limiting_enabled: bool = True
    requests_per_minute: int = 100
    burst_size: int = 20

    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    log_requests: bool = True
    log_responses: bool = False

    # Service URLs (for inter-service communication)
    auth_service_url: str = "http://localhost:8001"
    file_service_url: str = "http://localhost:8002"
    chat_service_url: str = "http://localhost:8003"
    collection_service_url: str = "http://localhost:8004"
    mcp_orchestrator_url: str = "http://localhost:8005"

    def __init__(self, **kwargs):
        # Load YAML configuration
        yaml_config = load_yaml_config()

        # Extract service-specific config if available
        # Use the class-level service_name or from kwargs
        service_name = kwargs.get(
            "service_name", getattr(self.__class__, "service_name", "unknown_service")
        )
        service_config = yaml_config.get("services", {}).get(service_name, {})

        # Merge YAML config with kwargs (kwargs take precedence)
        merged_config = {}

        # Map YAML structure to flat config
        if "database" in yaml_config:
            db_config = yaml_config["database"]
            merged_config.update(
                {
                    "db_pool_size": db_config.get("pool_size", 10),
                    "db_max_overflow": db_config.get("max_overflow", 20),
                    "db_echo": db_config.get("echo", False),
                }
            )

        if "redis" in yaml_config:
            redis_config = yaml_config["redis"]
            merged_config.update(
                {
                    "redis_db": redis_config.get("db", 0),
                    "redis_decode_responses": redis_config.get("decode_responses", True),
                }
            )

        if "cors" in yaml_config:
            cors_config = yaml_config["cors"]
            merged_config.update(
                {
                    "cors_origins": cors_config.get("origins", ["*"]),
                    "cors_methods": cors_config.get("methods", ["*"]),
                    "cors_headers": cors_config.get("headers", ["*"]),
                    "cors_credentials": cors_config.get("credentials", True),
                }
            )

        if "security" in yaml_config:
            security_config = yaml_config["security"]
            merged_config.update(
                {
                    "jwt_algorithm": security_config.get("jwt_algorithm", "HS256"),
                    "access_token_expire_minutes": security_config.get(
                        "access_token_expire_minutes", 30
                    ),
                    "refresh_token_expire_days": security_config.get(
                        "refresh_token_expire_days", 7
                    ),
                    "password_min_length": security_config.get("password_min_length", 8),
                    "max_login_attempts": security_config.get("max_login_attempts", 5),
                    "lockout_duration_minutes": security_config.get("lockout_duration_minutes", 15),
                }
            )

        if "rate_limiting" in yaml_config:
            rate_config = yaml_config["rate_limiting"]
            merged_config.update(
                {
                    "rate_limiting_enabled": rate_config.get("enabled", True),
                    "requests_per_minute": rate_config.get("requests_per_minute", 100),
                    "burst_size": rate_config.get("burst_size", 20),
                }
            )

        if "monitoring" in yaml_config:
            monitoring_config = yaml_config["monitoring"]
            merged_config.update(
                {
                    "enable_metrics": monitoring_config.get("enable_metrics", True),
                    "enable_tracing": monitoring_config.get("enable_tracing", True),
                    "log_requests": monitoring_config.get("log_requests", True),
                    "log_responses": monitoring_config.get("log_responses", False),
                }
            )

        # Service-specific overrides
        merged_config.update(service_config)

        # Environment variables and kwargs take precedence
        merged_config.update(kwargs)

        super().__init__(**merged_config)

    class Config:
        env_file = ".env"
        case_sensitive = False


class DatabaseServiceConfig(BaseServiceConfig):
    """Configuration for services that use external databases"""

    # Qdrant Configuration
    qdrant_url: str = Field(default="http://localhost:6335", env="QDRANT_URL")
    qdrant_grpc_port: int = 6336
    qdrant_timeout: int = 30
    qdrant_collection_name: str = "documents"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load Qdrant config from YAML
        yaml_config = load_yaml_config()
        if "qdrant" in yaml_config:
            qdrant_config = yaml_config["qdrant"]
            if not kwargs.get("qdrant_url"):
                host = qdrant_config.get("host", "localhost")
                port = qdrant_config.get("port", 6335)
                self.qdrant_url = f"http://{host}:{port}"
            self.qdrant_grpc_port = qdrant_config.get("grpc_port", 6336)
            self.qdrant_timeout = qdrant_config.get("timeout", 30)

    @property
    def qdrant_host(self) -> str:
        """Extract host from qdrant_url"""
        from urllib.parse import urlparse

        parsed = urlparse(self.qdrant_url)
        return parsed.hostname or "localhost"

    @property
    def qdrant_port(self) -> int:
        """Extract port from qdrant_url"""
        from urllib.parse import urlparse

        parsed = urlparse(self.qdrant_url)
        return parsed.port or 6333


class AIServiceConfig(DatabaseServiceConfig):
    """Configuration for services that use AI/ML models"""

    # LLM Configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    default_provider: str = "openai"
    default_model: str = "gpt-4"
    default_embedding_model: str = "text-embedding-3-small"
    llm_timeout: int = 60
    llm_max_retries: int = 3
    max_tokens: int = 4000
    temperature: float = 0.7

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load LLM config from YAML
        yaml_config = load_yaml_config()
        if "llm" in yaml_config:
            llm_config = yaml_config["llm"]
            self.default_provider = llm_config.get("default_provider", "openai")
            self.default_model = llm_config.get("default_model", "gpt-4")
            self.default_embedding_model = llm_config.get(
                "default_embedding_model", "text-embedding-3-small"
            )
            self.llm_timeout = llm_config.get("timeout", 60)
            self.llm_max_retries = llm_config.get("max_retries", 3)


class AuthServiceConfig(BaseServiceConfig):
    """Configuration specific to Auth Service"""

    service_name: str = "auth_service"
    port: int = 8001


class FileServiceConfig(AIServiceConfig):
    """Configuration specific to File Service"""

    service_name: str = "file_service"
    port: int = 8002

    # File Processing Configuration
    max_file_size_mb: int = 100
    allowed_extensions: List[str] = [".pdf", ".txt", ".docx", ".md", ".csv", ".json"]
    temp_dir: str = "/tmp/rag_uploads"
    cleanup_interval_hours: int = 24

    # Chunking Configuration
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load file processing config from YAML
        yaml_config = load_yaml_config()
        if "file_processing" in yaml_config:
            file_config = yaml_config["file_processing"]
            self.max_file_size_mb = file_config.get("max_file_size_mb", 100)
            self.allowed_extensions = file_config.get("allowed_extensions", self.allowed_extensions)
            self.temp_dir = file_config.get("temp_dir", "/tmp/rag_uploads")
            self.cleanup_interval_hours = file_config.get("cleanup_interval_hours", 24)


class ChatServiceConfig(AIServiceConfig):
    """Configuration specific to Chat Service"""

    service_name: str = "chat_service"
    port: int = 8003

    # Chat Configuration
    max_conversation_history: int = 50
    max_context_tokens: int = 8000
    default_top_k: int = 5
    stream_chunk_size: int = 1024

    # RAG Configuration
    context_merge_strategy: str = "enhanced_rrf"
    rrf_k: float = 60.0
    diversity_penalty: float = 0.1
    max_chunks_per_collection: int = 10

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load chat config from YAML
        yaml_config = load_yaml_config()
        if "chat" in yaml_config:
            chat_config = yaml_config["chat"]
            self.max_conversation_history = chat_config.get("max_conversation_history", 50)
            self.max_context_tokens = chat_config.get("max_context_tokens", 8000)
            self.default_top_k = chat_config.get("default_top_k", 5)
            self.stream_chunk_size = chat_config.get("stream_chunk_size", 1024)

        if "rag" in yaml_config:
            rag_config = yaml_config["rag"]
            self.context_merge_strategy = rag_config.get("context_merge_strategy", "enhanced_rrf")
            self.rrf_k = rag_config.get("rrf_k", 60.0)
            self.diversity_penalty = rag_config.get("diversity_penalty", 0.1)
            self.max_chunks_per_collection = rag_config.get("max_chunks_per_collection", 10)


class CollectionServiceConfig(BaseServiceConfig):
    """Configuration specific to Collection Service"""

    service_name: str = "collection_service"
    port: int = 8004

    # Collection Configuration
    max_collections_per_user: int = 100
    max_documents_per_collection: int = 10000
    max_collection_versions: int = 50

    # Default Collection Settings
    default_chunking_strategy: str = "recursive"
    default_chunk_size: int = 1000
    default_chunk_overlap: int = 200
    default_embedding_model: str = "text-embedding-3-small"

    # Version Control
    enable_version_auto_cleanup: bool = True
    version_cleanup_threshold: int = 30  # days

    # Collection Templates
    enable_collection_templates: bool = True
    default_system_prompt: str = (
        "You are a helpful AI assistant. Use the provided context to answer questions accurately and concisely."
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load collections config from YAML
        yaml_config = load_yaml_config()
        if "collections" in yaml_config:
            collections_config = yaml_config["collections"]
            self.max_collections_per_user = collections_config.get("max_per_user", 100)
            self.max_documents_per_collection = collections_config.get(
                "max_documents_per_collection", 10000
            )
            self.max_collection_versions = collections_config.get("max_versions", 50)
            self.default_chunking_strategy = collections_config.get(
                "default_chunking_strategy", "recursive"
            )
            self.default_chunk_size = collections_config.get("default_chunk_size", 1000)
            self.default_chunk_overlap = collections_config.get("default_chunk_overlap", 200)


class MCPOrchestratorConfig(BaseServiceConfig):
    """Configuration specific to MCP Orchestrator Service"""

    service_name: str = "mcp_orchestrator"
    port: int = 8005

    # MCP Configuration
    enable_tool_execution: bool = True
    tool_execution_timeout: int = 30
    max_concurrent_executions: int = 10
    enable_sandboxing: bool = True
    execution_environment: str = "docker"
    docker_image: str = "python:3.13-slim"
    docker_network: str = "bridge"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load MCP config from YAML
        yaml_config = load_yaml_config()
        if "mcp" in yaml_config:
            mcp_config = yaml_config["mcp"]
            self.enable_tool_execution = mcp_config.get("enable_tool_execution", True)
            self.tool_execution_timeout = mcp_config.get("tool_execution_timeout", 30)
            self.max_concurrent_executions = mcp_config.get("max_concurrent_executions", 10)
            self.enable_sandboxing = mcp_config.get("enable_sandboxing", True)
            self.execution_environment = mcp_config.get("execution_environment", "docker")
            self.docker_image = mcp_config.get("docker_image", "python:3.13-slim")
            self.docker_network = mcp_config.get("docker_network", "bridge")


# Service-specific configuration getters with caching
@lru_cache()
def get_auth_service_config() -> AuthServiceConfig:
    """Get Auth Service configuration (singleton)"""
    return AuthServiceConfig()


@lru_cache()
def get_file_service_config() -> FileServiceConfig:
    """Get File Service configuration (singleton)"""
    return FileServiceConfig()


@lru_cache()
def get_chat_service_config() -> ChatServiceConfig:
    """Get Chat Service configuration (singleton)"""
    return ChatServiceConfig()


@lru_cache()
def get_collection_service_config() -> CollectionServiceConfig:
    """Get Collection Service configuration (singleton)"""
    return CollectionServiceConfig()


@lru_cache()
def get_mcp_orchestrator_config() -> MCPOrchestratorConfig:
    """Get MCP Orchestrator configuration (singleton)"""
    return MCPOrchestratorConfig()


def get_service_config(service_name: str):
    """Get configuration for any service by name"""
    config_map = {
        "auth_service": get_auth_service_config,
        "file_service": get_file_service_config,
        "chat_service": get_chat_service_config,
        "collection_service": get_collection_service_config,
        "mcp_orchestrator": get_mcp_orchestrator_config,
    }

    config_getter = config_map.get(service_name)
    if not config_getter:
        raise ValueError(f"Unknown service: {service_name}")

    return config_getter()
