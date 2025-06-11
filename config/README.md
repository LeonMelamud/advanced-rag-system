# Configuration Management System

This directory contains the configuration management system for the Advanced RAG System, implementing a **simplified single-file approach** for environment variables.

## 🔒 Security Principle: Simplified Configuration Management

**UPDATED APPROACH**: This system uses a single `.env.{environment}` file approach in the project root, following 2024 Docker Compose best practices.

### Configuration Strategy

- **Environment Files** (`.env.*`): All configuration and secrets in root directory, **NEVER** version controlled
- **Configuration Files** (`environments/*.yaml`): Non-sensitive settings, version controlled

## 📁 Directory Structure

```
project_root/
├── .env.development          # Development environment (Docker Compose)
├── .env.testing             # Testing environment  
├── .env.staging             # Staging environment
├── .env.production          # Production environment
└── config/
    ├── environments/        # Non-sensitive configuration files (version controlled)
    │   ├── development.yaml # Development environment settings
    │   ├── testing.yaml     # Testing environment settings
    │   ├── staging.yaml     # Staging environment settings
    │   └── production.yaml  # Production environment settings
    └── README.md           # This documentation
```

## 🚀 Quick Setup

### 1. Environment Files Already Configured

Your `.env.development` file is already set up for Docker Compose with proper service names:
- Database: `postgres` (Docker service)
- Redis: `redis` (Docker service)  
- Qdrant: `qdrant` (Docker service)

### 2. Add Your API Keys

Edit the `.env.development` file and replace placeholder values:

```bash
# Example: Replace this line
OPENAI_API_KEY=sk-your_openai_api_key_here

# With your actual key
OPENAI_API_KEY=sk-proj-your_actual_openai_key_here
```

### 3. Restart Services

```bash
docker-compose restart chat_service
```

## 🔧 Environment-Specific Settings

### Development Environment (Current Setup)
- **Purpose**: Docker Compose development
- **Database**: Docker service `postgres:5432`
- **Redis**: Docker service `redis:6379`
- **Qdrant**: Docker service `qdrant:6333`
- **Logging**: DEBUG level with SQL logging enabled
- **Security**: Development-friendly settings

### Testing Environment
- **Purpose**: Automated testing and CI/CD
- **Database**: Separate test database (port 5434)
- **Redis**: Separate test Redis (port 6381)
- **Qdrant**: Separate test Qdrant (port 6337/6338)
- **Logging**: INFO level, minimal noise

### Staging Environment
- **Purpose**: Pre-production testing
- **Database**: Cloud database with staging credentials
- **Redis**: Cloud Redis with staging credentials
- **Qdrant**: Cloud Qdrant with staging credentials
- **Logging**: INFO level with monitoring enabled

### Production Environment
- **Purpose**: Live production system
- **Database**: Production database with high availability
- **Redis**: Production Redis with clustering
- **Qdrant**: Production Qdrant with clustering
- **Logging**: WARNING level, security-focused

## 🔐 Secret Management

### Development & Testing
- Use `.env.{environment}` files in project root
- Store in password manager or secure notes
- **NEVER** commit to version control (already in `.gitignore`)

### Staging & Production
- Use secure secret management systems:
  - **AWS**: AWS Secrets Manager, Parameter Store
  - **Azure**: Azure Key Vault
  - **GCP**: Google Secret Manager
  - **Kubernetes**: Kubernetes Secrets
  - **HashiCorp**: Vault

### Required Secrets by Environment

#### All Environments
- Database credentials (host, port, user, password)
- Redis credentials (host, port, password)
- Qdrant credentials (host, port, API key)
- JWT secret key
- LLM API keys (OpenAI, Gemini, Anthropic)

#### Development Additional (Already Configured)
- Docker service URLs
- Development API keys
- Local SMTP settings

#### Production Additional
- Production domain URLs
- Production API keys
- Production SMTP settings
- Monitoring credentials (Sentry)
- File storage credentials (AWS S3)
- OAuth provider credentials

## 🏗️ Configuration Loading

The system loads configuration in this order:

1. **Environment Variables**: Load from `.env.{ENVIRONMENT}`
2. **Base Configuration**: `environments/{ENVIRONMENT}.yaml`
3. **Override Variables**: Any shell environment variables

### Example Usage in Code

```python
from backend.common.config import get_config

# Load configuration for current environment
config = get_config()

# Access configuration values
db_host = config.database.host
redis_url = config.redis.url
jwt_secret = config.security.jwt_secret_key
```

## 🔄 Environment Switching

### Local Development (Docker Compose)

```bash
# Development (default)
docker-compose up

# Testing
ENVIRONMENT=testing docker-compose -f docker-compose.test.yml up

# Staging
ENVIRONMENT=staging docker-compose -f docker-compose.staging.yml up
```

### Kubernetes

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-proj-your-key-here"
  DB_PASSWORD: "your-secure-password"
```

## ✅ Current Status

- ✅ **Development Environment**: Fully configured for Docker Compose
- ✅ **Environment Variables**: Complete set in `.env.development`
- ✅ **Docker Integration**: Service names properly configured
- ✅ **Security**: File excluded from version control
- 🔧 **Action Required**: Add your actual OpenAI API key

## 🎯 Next Steps

1. **Add API Key**: Replace `sk-your_openai_api_key_here` with your actual OpenAI API key
2. **Test Chat Service**: Verify RAG pipeline works end-to-end
3. **Create Additional Environments**: Copy `.env.development` to `.env.testing`, `.env.staging`, `.env.production` as needed

---

**Updated**: January 2025 - Simplified to single-file approach following Docker Compose best practices 