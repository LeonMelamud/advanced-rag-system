# Advanced RAG System with File Analysis and AI Chat

A sophisticated Retrieval Augmented Generation (RAG) system designed to ingest, process, and understand diverse file types, making their content accessible through an intelligent AI chat interface.

## 🚀 Features

### Core Capabilities
- **Multi-Format File Processing**: Support for PDF, CSV, TXT, and Audio files (up to 100MB)
- **Advanced Text Extraction**: Robust extraction with metadata preservation
- **Audio Transcription**: Convert audio files to searchable text
- **Knowledge Collections**: Organize documents into logical, configurable collections
- **Multi-Collection Querying**: Search across multiple collections simultaneously
- **Intelligent Context Merging**: Enhanced Reciprocal Rank Fusion (RRF) algorithm
- **Real-time Chat Interface**: Streaming responses with source attribution
- **External Tools Integration**: Optional MCP protocol support

### Enterprise Features
- **Role-Based Access Control (RBAC)**: Secure collection and document access
- **Configuration Versioning**: Track and revert collection settings
- **Horizontal Scalability**: Microservices architecture with Kubernetes support
- **Comprehensive Monitoring**: Prometheus metrics and distributed tracing
- **High Availability**: Fault-tolerant design with backup/recovery

## 🏗️ Architecture

The system follows a microservices architecture with 6 core services:

1. **File Ingestion Service**: Handles file uploads and initial processing
2. **Data Processing Service**: Text extraction, chunking, and embedding generation
3. **Collection Management Service**: Manages knowledge collections and configurations
4. **Retrieval Service**: Vector search and context ranking
5. **Chat Orchestration Service**: LLM integration and conversation management
6. **Tools Integration Service**: External tools and MCP protocol support

### Technology Stack
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React with TypeScript
- **Vector Database**: Qdrant (primary), Pinecone/Weaviate (alternatives)
- **Metadata Database**: PostgreSQL
- **Cache**: Redis
- **Message Queue**: Redis/RabbitMQ
- **Container Orchestration**: Kubernetes
- **Monitoring**: Prometheus, Grafana, Jaeger

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18+ (for frontend)
- Docker and Docker Compose
- uv (Python package manager)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/leon-melamud/advanced-rag-system.git
cd advanced-rag-system
```

### 2. Install Python Dependencies with uv
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install core dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"

# Install optional dependencies (choose as needed)
uv pip install -e ".[prod]"      # Production dependencies
uv pip install -e ".[tools]"     # External tools integration
uv pip install -e ".[ml-advanced]"  # Advanced ML features
```

### 3. Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# - Database URLs
# - API keys (OpenAI, Gemini, etc.)
# - Vector database settings
# - Authentication settings
```

### 4. Database Setup
```bash
# Start PostgreSQL and Qdrant with Docker Compose
docker-compose up -d postgres qdrant redis

# Run database migrations
cd backend
alembic upgrade head
```

### 5. Development Setup
```bash
# Install pre-commit hooks
pre-commit install

# Run code formatting
black backend/
isort backend/

# Run tests
pytest backend/
```

## 🚀 Quick Start

### Using the DRY Build System (Makefile)

The project uses a comprehensive Makefile for all build and development operations:

```bash
# View all available commands
make help

# Build all services (recommended for first setup)
make build-all

# Build individual services
make build-auth          # Auth service
make build-chat          # Chat service  
make build-collection    # Collection service
make build-file          # File service
make build-mcp           # MCP orchestrator

# Development workflow
make up                  # Start all services with docker-compose
make down                # Stop all services
make restart             # Restart all services
make status              # Check service status

# Service management
make run-service SERVICE=auth_service     # Run specific service
make stop-service SERVICE=auth_service    # Stop specific service
make logs SERVICE=auth_service            # View service logs

# Development helpers
make test                # Run tests
make health-check        # Check all service health
make dev-setup          # Complete development setup

# Cleanup
make clean              # Remove service images
make clean-all          # Remove all images including base
```

### Development Mode
```bash
# Complete development setup
make dev-setup

# Start all services
make up

# Check everything is running
make status
make health-check
```

### Production Mode
```bash
# Build and deploy with Kubernetes
kubectl apply -f deploy/kubernetes/

# Or use Docker Compose for simpler deployments
docker-compose -f deploy/docker-compose.prod.yml up -d
```

## 📖 Usage

### 1. Create a Knowledge Collection
```python
import httpx

# Create a new collection
collection_data = {
    "config": {
        "name": "Technical Documentation",
        "description": "Company technical docs and manuals",
        "system_prompt": "You are a helpful technical assistant...",
        "llm_model": "gpt-4",
        "embedding_model": "text-embedding-3-large",
        "chunking_strategy": "recursive",
        "chunking_params": {"chunk_size": 1000, "overlap": 200}
    },
    "is_public": False,
    "tags": ["technical", "documentation"]
}

response = httpx.post("http://localhost:8000/api/v1/collections", json=collection_data)
collection = response.json()
```

### 2. Upload Documents
```python
# Upload a PDF file
files = {"file": open("manual.pdf", "rb")}
data = {"collection_ids": [collection["id"]]}

response = httpx.post("http://localhost:8000/api/v1/files/upload", files=files, data=data)
upload_result = response.json()
```

### 3. Chat with Your Documents
```python
# Start a chat session
chat_data = {
    "message": "How do I configure the authentication system?",
    "collection_ids": [collection["id"]],
    "stream": True
}

response = httpx.post("http://localhost:8000/api/v1/chat", json=chat_data)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

## 📊 Performance Targets

- **File Ingestion**: < 5 seconds per MB of text content
- **Query Preprocessing**: < 100ms (P95)
- **Context Retrieval**: < 750ms (P95)
- **LLM First Token**: < 1.5s (P95)
- **End-to-End Response**: < 3.0s (P95)
- **Concurrent Queries**: 50 QPS

## 🔧 Configuration Management

### 🔒 Separation of Concerns Principle

This system implements **strict separation of concerns** between configuration settings and sensitive secrets:

- **Configuration Files** (`config/environments/*.yaml`): Non-sensitive settings, version controlled
- **Secret Files** (`.env.*`): Sensitive keys and credentials, **NEVER** version controlled

### Quick Setup

1. **Choose Your Environment**:
   ```bash
   # Development
   cp config/secrets/env.development.template .env.development
   
   # Testing  
   cp config/secrets/env.testing.template .env.testing
   
   # Staging
   cp config/secrets/env.staging.template .env.staging
   
   # Production
   cp config/secrets/env.production.template .env.production
   ```

2. **Fill in Your Secrets**: Edit the `.env.*` file and replace all placeholder values
3. **Set Environment**: `export ENVIRONMENT=development`

### Environment-Specific Settings

| Environment | Purpose | Database Port | Redis Port | Qdrant Port | Log Level |
|-------------|---------|---------------|------------|-------------|-----------|
| Development | Local dev & debugging | 5433 | 6380 | 6335/6336 | DEBUG |
| Testing | Automated testing | 5434 | 6381 | 6337/6338 | INFO |
| Staging | Pre-production testing | Cloud | Cloud | Cloud | INFO |
| Production | Live system | Cloud | Cloud | Cloud | WARNING |

### Required Secrets

#### All Environments
- Database credentials (host, port, user, password)
- Redis credentials (host, port, password)  
- Qdrant credentials (host, port, API key)
- JWT secret key
- LLM API keys (OpenAI, Gemini, Anthropic)

#### Production Additional
- Production domain URLs
- Monitoring credentials (Sentry)
- File storage credentials (AWS S3)
- OAuth provider credentials

### Security Best Practices

1. **Never Commit Secrets**: `.env*` files are in `.gitignore`
2. **Use Strong Secrets**: Generate with `openssl rand -hex 32`
3. **Rotate Regularly**: Weekly in production, monthly in development
4. **Use Secret Management**: AWS Secrets Manager, Azure Key Vault, etc. for production

📖 **Full Documentation**: See [`config/README.md`](config/README.md) for complete configuration management guide.

## 🔧 Legacy Configuration (Deprecated)

### Environment Variables

## 🔍 Monitoring

### Health Checks
```bash
# Check system health
curl http://localhost:8000/health

# Check individual service health
curl http://localhost:8001/health  # File service
curl http://localhost:8002/health  # Chat service
```

### Metrics
- Prometheus metrics available at `/metrics` endpoint
- Grafana dashboards in `deploy/monitoring/`
- Jaeger tracing at `http://localhost:16686`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide
- Write comprehensive tests
- Update documentation
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for RAG framework inspiration
- [Qdrant](https://qdrant.tech/) for vector database capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [React](https://reactjs.org/) for the frontend framework

## 📞 Support

- 📧 Email: leon.melamud@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/leon-melamud/advanced-rag-system/issues)
- 📖 Documentation: [Project Wiki](https://github.com/leon-melamud/advanced-rag-system/wiki)

---

**Built with ❤️ for intelligent document processing and AI-powered conversations.** 