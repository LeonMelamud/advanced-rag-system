# Advanced RAG System - API Documentation

## Overview

This document provides comprehensive API documentation for the Advanced RAG System microservices architecture. The system consists of 5 core services, each with their own REST API endpoints.

## Service Architecture

### Core Services

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| **Auth Service** | 8001 | User authentication, JWT tokens, RBAC | `/health/liveness` |
| **File Service** | 8002 | File processing, chunking, embedding | `/health/liveness` |
| **Chat Service** | 8003 | RAG orchestration, streaming chat | `/health/liveness` |
| **Collection Service** | 8004 | Knowledge collection management | `/health/liveness` |
| **MCP Orchestrator** | 8005 | Tool management and execution | `/health/liveness` |

### API Gateway

| Component | Port | Purpose |
|-----------|------|---------|
| **API Gateway** | 8000 | Request routing, load balancing, CORS |

## Authentication Flow

All services use JWT-based authentication provided by the Auth Service:

1. **Login**: `POST /api/v1/auth/login` → Returns JWT token
2. **Token Validation**: Include `Authorization: Bearer <token>` header
3. **Token Refresh**: `POST /api/v1/auth/refresh` → Returns new token

## API Endpoints by Service

### Auth Service (Port 8001)

#### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user info

#### User Management
- `GET /api/v1/users/` - List users (admin only)
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

#### Health Checks
- `GET /health/liveness` - Service liveness probe
- `GET /health/readiness` - Service readiness probe
- `GET /health/detailed` - Detailed health information

### File Service (Port 8002)

#### File Management
- `POST /api/v1/files/upload` - Upload file for processing
- `GET /api/v1/files/` - List user files
- `GET /api/v1/files/{file_id}` - Get file details
- `DELETE /api/v1/files/{file_id}` - Delete file
- `GET /api/v1/files/{file_id}/download` - Download file

#### File Processing
- `POST /api/v1/files/{file_id}/process` - Process file (chunking, embedding)
- `GET /api/v1/files/{file_id}/chunks` - Get file chunks
- `GET /api/v1/files/{file_id}/status` - Get processing status

#### Health Checks
- `GET /health/liveness` - Service liveness probe
- `GET /health/readiness` - Service readiness probe
- `GET /health/detailed` - Detailed health information

### Chat Service (Port 8003)

#### Chat Sessions
- `POST /api/v1/sessions/` - Create chat session
- `GET /api/v1/sessions/` - List user sessions
- `GET /api/v1/sessions/{session_id}` - Get session details
- `PUT /api/v1/sessions/{session_id}` - Update session
- `DELETE /api/v1/sessions/{session_id}` - Delete session

#### Chat Messages
- `POST /api/v1/chat/message` - Send message (non-streaming)
- `POST /api/v1/chat/stream` - Send message (streaming)
- `GET /api/v1/chat/history/{session_id}` - Get chat history

#### Health Checks
- `GET /health/liveness` - Service liveness probe
- `GET /health/readiness` - Service readiness probe
- `GET /health/detailed` - Detailed health information

### Collection Service (Port 8004)

#### Collection Management
- `POST /api/v1/collections/` - Create collection
- `GET /api/v1/collections/` - List collections
- `GET /api/v1/collections/{collection_id}` - Get collection details
- `PUT /api/v1/collections/{collection_id}` - Update collection
- `DELETE /api/v1/collections/{collection_id}` - Archive collection

#### Collection Statistics
- `GET /api/v1/collections/{collection_id}/stats` - Collection statistics
- `GET /api/v1/collections/{collection_id}/config` - Collection configuration

#### Access Control
- `GET /api/v1/collections/{collection_id}/access` - List access permissions
- `POST /api/v1/collections/{collection_id}/access` - Grant access
- `DELETE /api/v1/collections/{collection_id}/access/{user_id}` - Revoke access

#### Versioning
- `GET /api/v1/versions/` - List collection versions
- `GET /api/v1/versions/{version_id}` - Get version details

#### Health Checks
- `GET /health/liveness` - Service liveness probe
- `GET /health/readiness` - Service readiness probe
- `GET /health/detailed` - Detailed health information

### MCP Orchestrator (Port 8005)

#### Tool Management
- `POST /api/v1/tools/` - Create tool
- `GET /api/v1/tools/` - List tools
- `GET /api/v1/tools/{tool_id}` - Get tool details
- `PUT /api/v1/tools/{tool_id}` - Update tool
- `DELETE /api/v1/tools/{tool_id}` - Delete tool

#### Tool Statistics
- `GET /api/v1/tools/{tool_id}/stats` - Tool execution statistics

#### Tool Access Control
- `GET /api/v1/tools/{tool_id}/access` - List tool access
- `POST /api/v1/tools/{tool_id}/access` - Grant tool access
- `DELETE /api/v1/tools/{tool_id}/access/{user_id}` - Revoke tool access

#### Tool Execution
- `POST /api/v1/executions/` - Create execution
- `GET /api/v1/executions/` - List user executions
- `GET /api/v1/executions/{execution_id}` - Get execution details
- `GET /api/v1/executions/tools/{tool_id}` - List tool executions

#### Health Checks
- `GET /health/liveness` - Service liveness probe
- `GET /health/readiness` - Service readiness probe
- `GET /health/detailed` - Detailed health information

## OpenAPI/Swagger Documentation

Each service provides interactive API documentation:

- **Auth Service**: http://localhost:8001/docs
- **File Service**: http://localhost:8002/docs
- **Chat Service**: http://localhost:8003/docs
- **Collection Service**: http://localhost:8004/docs
- **MCP Orchestrator**: http://localhost:8005/docs

## Error Handling

All services use standardized error responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `204` - No Content
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
- `503` - Service Unavailable

## Rate Limiting

API rate limiting is implemented at the gateway level:

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- **Admin**: 10000 requests per minute

## CORS Configuration

CORS is configured to allow:

- **Origins**: Configurable per environment
- **Methods**: GET, POST, PUT, DELETE, OPTIONS
- **Headers**: Authorization, Content-Type, Accept
- **Credentials**: Enabled for authenticated requests

## Testing

### Health Check Testing

```bash
# Test all service health endpoints
curl http://localhost:8001/health/liveness
curl http://localhost:8002/health/liveness
curl http://localhost:8003/health/liveness
curl http://localhost:8004/health/liveness
curl http://localhost:8005/health/liveness
```

### Authentication Testing

```bash
# Register a new user
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Login to get JWT token
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Service Integration Testing

```bash
# Test service communication
curl -H "Authorization: Bearer <token>" http://localhost:8002/api/v1/files/
curl -H "Authorization: Bearer <token>" http://localhost:8003/api/v1/sessions/
curl -H "Authorization: Bearer <token>" http://localhost:8004/api/v1/collections/
curl -H "Authorization: Bearer <token>" http://localhost:8005/api/v1/tools/
```

## Development

### Local Development Setup

1. **Start Services**: `docker-compose up -d`
2. **Check Status**: `docker-compose ps`
3. **View Logs**: `docker-compose logs <service_name>`
4. **Stop Services**: `docker-compose down`

### Environment Variables

Key environment variables for API configuration:

- `JWT_SECRET_KEY` - JWT signing key
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_EXPIRE_MINUTES` - Token expiration (default: 30)
- `CORS_ORIGINS` - Allowed CORS origins
- `API_RATE_LIMIT` - Rate limiting configuration

## Monitoring

### Health Monitoring

All services provide three levels of health checks:

1. **Liveness**: Basic service availability
2. **Readiness**: Service ready to handle requests
3. **Detailed**: Comprehensive dependency status

### Metrics

Services expose metrics for monitoring:

- Request count and latency
- Error rates by endpoint
- Database connection status
- Cache hit/miss rates
- Queue depth and processing time

## Security

### Authentication Security

- JWT tokens with configurable expiration
- Password hashing with bcrypt
- Role-based access control (RBAC)
- Session management with Redis

### API Security

- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- XSS protection with proper headers
- Rate limiting and DDoS protection

### Data Security

- Encryption at rest for sensitive data
- TLS encryption for data in transit
- Audit logging for security events
- Secure secret management

## Troubleshooting

### Common Issues

1. **Service Not Starting**: Check Docker logs and dependencies
2. **Authentication Failures**: Verify JWT configuration
3. **Database Errors**: Check PostgreSQL connection
4. **Performance Issues**: Monitor resource usage and query performance

### Debug Endpoints

Development environment includes debug endpoints:

- `GET /debug/config` - Service configuration
- `GET /debug/health` - Extended health information
- `GET /debug/metrics` - Service metrics

---

**Last Updated**: 2024-12-19  
**Version**: 1.0.0  
**Status**: Week 2 Implementation - API Documentation Complete 