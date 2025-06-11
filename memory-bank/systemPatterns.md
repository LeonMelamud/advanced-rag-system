# System Patterns

## Debugging and Troubleshooting Patterns

### 1. Error Resolution Research Pattern
**Context**: When encountering code errors, dependency issues, or implementation challenges
**Pattern**: Systematic research using external knowledge sources before manual debugging
**Implementation**:
```
1. Identify the specific error or issue
2. Use Brave Search MCP for current documentation and solutions
3. Use Context7 MCP for library-specific documentation and examples
4. Search for error messages, library versions, and platform-specific issues
5. Look for recent solutions (include current date in searches)
6. Apply solutions and document successful approaches
```
**Tools Available**:
- `mcp_brave-search_brave_web_search`: For general web search and recent solutions
- `mcp_context7-mcp_resolve-library-id`: To find correct library documentation
- `mcp_context7-mcp_get-library-docs`: For specific library documentation and examples
**Benefits**: Faster resolution, current solutions, comprehensive documentation access
**Usage**: All error scenarios, dependency conflicts, implementation questions

### 2. Documentation-First Debugging
**Context**: Understanding proper usage patterns and best practices
**Pattern**: Consult official documentation before attempting fixes
**Implementation**:
```python
# Before implementing, check:
# 1. Official library documentation via Context7
# 2. Recent changes and updates via Brave search
# 3. Platform-specific considerations
# 4. Version compatibility issues
```
**Benefits**: Correct implementation, avoiding deprecated patterns
**Usage**: New library integration, version upgrades, platform changes

### 3. Version-Aware Problem Solving
**Context**: Dependency conflicts and version compatibility issues
**Pattern**: Include version information and dates in searches
**Implementation**:
```
Search patterns:
- "library_name version_number error_message 2025"
- "Python 3.13 compatibility library_name"
- "latest documentation library_name installation"
```
**Benefits**: Current and relevant solutions
**Usage**: Installation issues, compatibility problems, deprecated features

## Architectural Patterns

### 1. Microservices Pattern
**Context**: Complex system with diverse technical requirements and independent scaling needs
**Pattern**: Decompose application into loosely coupled, independently deployable services
**Implementation**:
```
- Service per business capability (auth, file processing, chat, collections)
- API Gateway for unified entry point
- Service mesh for inter-service communication
- Database per service for data isolation
```
**Benefits**: Independent scaling, technology diversity, fault isolation
**Trade-offs**: Increased operational complexity, network latency

### 2. Event-Driven Architecture
**Context**: Asynchronous processing pipelines and loose coupling between services
**Pattern**: Services communicate through events rather than direct calls
**Implementation**:
```
- Message queues (Redis/RabbitMQ) for async processing
- Event sourcing for audit trails
- Pub/Sub for real-time notifications
- Saga pattern for distributed transactions
```
**Benefits**: Loose coupling, scalability, resilience
**Trade-offs**: Eventual consistency, debugging complexity

### 3. CQRS (Command Query Responsibility Segregation)
**Context**: Different read and write patterns for vector data vs metadata
**Pattern**: Separate read and write models for optimal performance
**Implementation**:
```
- Write model: Optimized for document ingestion and updates
- Read model: Optimized for search and retrieval operations
- Event-driven synchronization between models
```
**Benefits**: Optimized performance, independent scaling
**Trade-offs**: Increased complexity, eventual consistency

## Design Patterns

### 1. Repository Pattern
**Context**: Data access abstraction across different storage systems
**Pattern**: Encapsulate data access logic behind repository interfaces
**Implementation**:
```python
class VectorRepository(ABC):
    @abstractmethod
    async def search(self, query_vector: List[float], top_k: int) -> List[SearchResult]:
        pass
    
    @abstractmethod
    async def insert(self, vectors: List[VectorData]) -> bool:
        pass

class QdrantRepository(VectorRepository):
    # Qdrant-specific implementation
    
class PineconeRepository(VectorRepository):
    # Pinecone-specific implementation
```
**Benefits**: Database agnostic code, testability, flexibility
**Usage**: All data access layers

### 2. Factory Pattern
**Context**: Creating different embedding models and vector databases
**Pattern**: Create objects without specifying exact classes
**Implementation**:
```python
class EmbeddingModelFactory:
    @staticmethod
    def create_model(model_type: str, config: Dict) -> EmbeddingModel:
        if model_type == "openai":
            return OpenAIEmbeddingModel(config)
        elif model_type == "gemini":
            return GeminiEmbeddingModel(config)
        # ... other models

class VectorDBFactory:
    @staticmethod
    def create_client(db_type: str, config: Dict) -> VectorRepository:
        if db_type == "qdrant":
            return QdrantRepository(config)
        elif db_type == "pinecone":
            return PineconeRepository(config)
        # ... other databases
```
**Benefits**: Flexibility, configuration-driven instantiation
**Usage**: Model creation, database client creation

### 3. Strategy Pattern
**Context**: Different chunking strategies and merging algorithms
**Pattern**: Define family of algorithms and make them interchangeable
**Implementation**:
```python
class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk_text(self, text: str) -> List[str]:
        pass

class RecursiveChunkingStrategy(ChunkingStrategy):
    def chunk_text(self, text: str) -> List[str]:
        # Recursive chunking implementation
        pass

class SemanticChunkingStrategy(ChunkingStrategy):
    def chunk_text(self, text: str) -> List[str]:
        # Semantic chunking implementation
        pass

class DocumentProcessor:
    def __init__(self, chunking_strategy: ChunkingStrategy):
        self.chunking_strategy = chunking_strategy
```
**Benefits**: Algorithm flexibility, runtime selection
**Usage**: Document processing, context merging, ranking algorithms

### 4. Observer Pattern
**Context**: Real-time updates and notifications across services
**Pattern**: Define one-to-many dependency between objects
**Implementation**:
```python
class DocumentProcessingObserver(ABC):
    @abstractmethod
    async def on_processing_complete(self, document_id: str, status: str):
        pass

class DocumentProcessor:
    def __init__(self):
        self.observers: List[DocumentProcessingObserver] = []
    
    def add_observer(self, observer: DocumentProcessingObserver):
        self.observers.append(observer)
    
    async def notify_observers(self, document_id: str, status: str):
        for observer in self.observers:
            await observer.on_processing_complete(document_id, status)
```
**Benefits**: Loose coupling, extensibility
**Usage**: Processing notifications, real-time updates

## Data Patterns

### 1. Collection-per-Tenant Pattern
**Context**: Multi-tenant vector database with isolation requirements
**Pattern**: Separate vector collections for each Knowledge Collection
**Implementation**:
```
Collection Naming: knowledge_collection_{collection_id}
Isolation: Physical separation at database level
Access Control: Collection-level permissions
Configuration: Per-collection embedding models and parameters
```
**Benefits**: True isolation, independent optimization, security
**Trade-offs**: Management overhead, cross-collection queries complexity

### 2. Metadata Enrichment Pattern
**Context**: Rich metadata for filtering and attribution
**Pattern**: Store comprehensive metadata alongside vectors
**Implementation**:
```json
{
  "vector": [0.1, 0.2, ...],
  "metadata": {
    "document_id": "doc_123",
    "chunk_id": "chunk_456", 
    "source_filename": "report.pdf",
    "file_type": "PDF",
    "created_at": "2024-01-15T10:30:00Z",
    "custom_metadata": {...}
  }
}
```
**Benefits**: Rich filtering, source attribution, analytics
**Usage**: All vector storage operations

### 3. Hierarchical Caching Pattern
**Context**: Performance optimization for frequently accessed data
**Pattern**: Multi-level caching with different TTLs and strategies
**Implementation**:
```
Level 1: In-memory LRU cache (query results, embeddings)
Level 2: Redis distributed cache (session data, user preferences)
Level 3: Database query optimization (connection pooling, prepared statements)
```
**Benefits**: Reduced latency, improved throughput
**Usage**: Query results, embeddings, session data

## API Patterns

### 1. RESTful Resource Pattern
**Context**: Standard CRUD operations for business entities
**Pattern**: Resource-based URLs with HTTP verbs
**Implementation**:
```
GET    /api/v1/collections          # List collections
POST   /api/v1/collections          # Create collection
GET    /api/v1/collections/{id}     # Get collection
PUT    /api/v1/collections/{id}     # Update collection
DELETE /api/v1/collections/{id}     # Delete collection

GET    /api/v1/collections/{id}/documents  # List documents in collection
POST   /api/v1/collections/{id}/documents  # Add document to collection
```
**Benefits**: Predictable, standard, cacheable
**Usage**: All CRUD operations

### 2. Command Pattern for APIs
**Context**: Complex operations that don't fit REST model
**Pattern**: Action-based endpoints for business operations
**Implementation**:
```
POST /api/v1/collections/{id}/search     # Search within collection
POST /api/v1/chat/sessions/{id}/message  # Send chat message
POST /api/v1/documents/{id}/reprocess    # Reprocess document
POST /api/v1/collections/{id}/merge      # Merge collections
```
**Benefits**: Clear intent, complex operations support
**Usage**: Search, chat, processing operations

### 3. Streaming Response Pattern
**Context**: Real-time chat responses and large data transfers
**Pattern**: Server-Sent Events or WebSockets for streaming
**Implementation**:
```python
@app.get("/api/v1/chat/stream/{session_id}")
async def stream_chat_response(session_id: str):
    async def generate():
        async for chunk in llm_client.stream_response(query):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")
```
**Benefits**: Real-time updates, better user experience
**Usage**: Chat responses, file upload progress, processing status

## Security Patterns

### 1. JWT Token Pattern
**Context**: Stateless authentication across microservices
**Pattern**: JSON Web Tokens for authentication and authorization
**Implementation**:
```python
# Token structure
{
  "sub": "user_id",
  "roles": ["user", "admin"],
  "collections": ["collection_1", "collection_2"],
  "exp": 1640995200,
  "iat": 1640908800
}

# Middleware validation
async def verify_jwt_token(token: str) -> UserContext:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return UserContext(
        user_id=payload["sub"],
        roles=payload["roles"],
        accessible_collections=payload["collections"]
    )
```
**Benefits**: Stateless, scalable, secure
**Usage**: All API authentication

### 2. Role-Based Access Control (RBAC)
**Context**: Fine-grained permissions for different user types
**Pattern**: Roles with permissions, users assigned to roles
**Implementation**:
```python
class Permission(Enum):
    READ_COLLECTION = "read:collection"
    WRITE_COLLECTION = "write:collection"
    ADMIN_COLLECTION = "admin:collection"
    CHAT_ACCESS = "chat:access"

class Role:
    name: str
    permissions: List[Permission]

# Usage in endpoints
@require_permission(Permission.READ_COLLECTION)
async def get_collection(collection_id: str, user: UserContext):
    # Verify user has access to specific collection
    if collection_id not in user.accessible_collections:
        raise HTTPException(403, "Access denied")
```
**Benefits**: Fine-grained control, scalable permissions
**Usage**: All protected endpoints

## Error Handling Patterns

### 1. Structured Error Response Pattern
**Context**: Consistent error handling across all services
**Pattern**: Standardized error response format
**Implementation**:
```python
class APIError(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str

# Usage
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content=APIError(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": exc.errors()},
            timestamp=datetime.utcnow(),
            request_id=request.headers.get("X-Request-ID")
        ).dict()
    )
```
**Benefits**: Consistent error handling, better debugging
**Usage**: All API endpoints

### 2. Circuit Breaker Pattern
**Context**: Resilience against external service failures
**Pattern**: Prevent cascading failures through circuit breaking
**Implementation**:
```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenError()
        
        try:
            result = await func(*args, **kwargs)
            self.reset()
            return result
        except Exception as e:
            self.record_failure()
            raise e
```
**Benefits**: System resilience, graceful degradation
**Usage**: External API calls, database connections

## Performance Patterns

### 1. Connection Pooling Pattern
**Context**: Efficient database and external service connections
**Pattern**: Reuse connections to reduce overhead
**Implementation**:
```python
# Database connection pool
DATABASE_POOL = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# HTTP client pool
HTTP_CLIENT = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
    timeout=httpx.Timeout(30.0)
)
```
**Benefits**: Reduced latency, better resource utilization
**Usage**: Database connections, HTTP clients

### 2. Batch Processing Pattern
**Context**: Efficient processing of large datasets
**Pattern**: Process items in batches to optimize throughput
**Implementation**:
```python
async def process_documents_in_batches(documents: List[Document], batch_size: int = 10):
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        
        # Process batch concurrently
        tasks = [process_document(doc) for doc in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and errors
        for doc, result in zip(batch, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process {doc.id}: {result}")
            else:
                logger.info(f"Successfully processed {doc.id}")
```
**Benefits**: Better throughput, controlled resource usage
**Usage**: Document processing, embedding generation, bulk operations

---
*Last Updated: Current Session*
*Next Update: As new patterns are identified and implemented*

# SYSTEM PATTERNS - ADVANCED RAG SYSTEM

## 🎯 MANDATORY PRE-CHANGE CHECKLIST

### **BEFORE MAKING ANY FILE CHANGES - ALWAYS CHECK:**

1. **📋 Check @project_structure.md FIRST**
   - Understand current file organization
   - Identify existing shared components
   - Verify if similar functionality already exists
   - Check for base classes or shared patterns

2. **🔍 Look for Existing Shared Components**
   - `backend/common/` - Shared utilities and base classes
   - `@Dockerfile.base` - Shared Docker configuration
   - `backend/common/service_factory.py` - DRY service creation
   - `backend/common/main_base.py` - Base service application

3. **🚫 NEVER Duplicate What Already Exists**
   - If there's a base Dockerfile, use it properly
   - If there's a shared component, extend it
   - If there's a pattern, follow it consistently
   - If there's a factory, use it instead of creating new classes

4. **✅ DRY Principle Enforcement**
   - Can I use an existing base class?
   - Can I extend a shared component?
   - Can I configure rather than duplicate?
   - Is there a pattern I should follow?

## 🏗️ ESTABLISHED PATTERNS

### **Docker Architecture Pattern**
- **Base Image**: `@Dockerfile.base` handles all common setup
- **Service Images**: Should only add service-specific dependencies
- **Volume Mounts**: Use proper paths that align with base image structure
- **Python Path**: Already configured in base image

### **Service Creation Pattern**
- **Factory Pattern**: Use `create_service_app()` from `service_factory.py`
- **No Custom Classes**: Eliminate service-specific app classes
- **Configuration**: Pass settings and routers to factory
- **Consistency**: All services follow identical pattern

### **Shared Components Pattern**
- **Common Directory**: All shared code in `backend/common/`
- **Base Classes**: Extend `BaseServiceApp` through factory
- **Utilities**: Use shared utilities for common operations
- **Configuration**: Use shared config management

## 🔄 VIOLATION PREVENTION

### **Red Flags - Stop and Check:**
- Copying similar code across files
- Creating new classes when base classes exist
- Modifying multiple Dockerfiles for same change
- Adding dependencies that might already exist
- Creating patterns that duplicate existing ones

### **Green Flags - Good DRY Practice:**
- Using existing base classes and factories
- Extending shared components
- Following established patterns
- Configuring rather than duplicating
- Checking project structure before changes

---

**Remember**: The project structure document is the single source of truth. Always consult it before making changes to understand what already exists and how to properly extend it. 