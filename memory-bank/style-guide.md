# Style Guide

## Python Code Standards

### General Principles
- **Readability**: Code should be self-documenting and easy to understand
- **Consistency**: Follow established patterns throughout the codebase
- **Simplicity**: Prefer simple, explicit solutions over clever, implicit ones
- **Type Safety**: Use type hints extensively for better IDE support and documentation

### Code Formatting
- **Tool**: Use `ruff format` (black-compatible) for automatic formatting
- **Line Length**: 88 characters maximum (black default)
- **Quotes**: Double quotes for strings, single quotes for string literals in code
- **Imports**: Use `ruff` for import sorting and organization

### Naming Conventions

#### Variables and Functions
```python
# Use snake_case for variables and functions
user_id = "12345"
collection_name = "documents"

def process_document(document: Document) -> ProcessedDocument:
    """Process a document and return the result."""
    pass

def get_user_collections(user_id: str) -> List[Collection]:
    """Retrieve all collections accessible to a user."""
    pass
```

#### Classes
```python
# Use PascalCase for class names
class DocumentProcessor:
    """Handles document processing operations."""
    pass

class VectorSearchEngine:
    """Manages vector similarity search operations."""
    pass

class UserCollectionManager:
    """Manages user access to collections."""
    pass
```

#### Constants
```python
# Use UPPER_SNAKE_CASE for constants
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
DEFAULT_CHUNK_SIZE = 1000
SUPPORTED_FILE_TYPES = ["pdf", "txt", "csv", "mp3", "wav"]
API_VERSION = "v1"
```

#### Private Members
```python
class DocumentProcessor:
    def __init__(self):
        self._internal_state = {}  # Single underscore for internal use
        self.__private_data = {}   # Double underscore for name mangling
    
    def _helper_method(self) -> str:
        """Internal helper method."""
        pass
```

### Type Hints
```python
from typing import List, Dict, Optional, Union, Any, Callable
from pydantic import BaseModel

# Always use type hints for function parameters and return values
def search_documents(
    query: str,
    collection_ids: List[str],
    limit: int = 10,
    filters: Optional[Dict[str, Any]] = None
) -> List[SearchResult]:
    """Search for documents across multiple collections."""
    pass

# Use Pydantic models for data structures
class SearchRequest(BaseModel):
    query: str
    collection_ids: List[str]
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    document_id: str
    score: float
    content: str
    metadata: Dict[str, Any]
```

### Error Handling
```python
# Use specific exception types
class DocumentProcessingError(Exception):
    """Raised when document processing fails."""
    pass

class CollectionNotFoundError(Exception):
    """Raised when a collection cannot be found."""
    pass

# Proper exception handling with logging
import logging

logger = logging.getLogger(__name__)

async def process_document(document: Document) -> ProcessedDocument:
    try:
        result = await _extract_text(document)
        return result
    except FileNotFoundError:
        logger.error(f"Document file not found: {document.filename}")
        raise DocumentProcessingError(f"File not found: {document.filename}")
    except Exception as e:
        logger.exception(f"Unexpected error processing document {document.id}")
        raise DocumentProcessingError(f"Processing failed: {str(e)}")
```

### Async/Await Patterns
```python
# Prefer async/await for I/O operations
async def fetch_embeddings(texts: List[str]) -> List[List[float]]:
    """Fetch embeddings for multiple texts concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [_get_embedding(client, text) for text in texts]
        results = await asyncio.gather(*tasks)
        return results

# Use context managers for resource management
async def process_file(file_path: str) -> ProcessedFile:
    async with aiofiles.open(file_path, 'rb') as file:
        content = await file.read()
        return await _process_content(content)
```

### Documentation
```python
def search_collections(
    query: str,
    collection_ids: List[str],
    top_k: int = 10
) -> List[SearchResult]:
    """
    Search for relevant documents across multiple collections.
    
    Args:
        query: The search query string
        collection_ids: List of collection IDs to search within
        top_k: Maximum number of results to return (default: 10)
    
    Returns:
        List of SearchResult objects ordered by relevance score
    
    Raises:
        CollectionNotFoundError: If any collection ID is invalid
        SearchEngineError: If the search operation fails
    
    Example:
        >>> results = search_collections(
        ...     query="machine learning",
        ...     collection_ids=["tech-docs", "research-papers"],
        ...     top_k=5
        ... )
        >>> len(results)
        5
    """
    pass
```

## FastAPI Patterns

### API Endpoint Structure
```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/collections", tags=["collections"])

class CreateCollectionRequest(BaseModel):
    name: str
    description: Optional[str] = None
    embedding_model: str = "gemini"

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    document_count: int

@router.post("/", response_model=CollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    request: CreateCollectionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> CollectionResponse:
    """
    Create a new knowledge collection.
    
    - **name**: Collection name (required)
    - **description**: Optional description
    - **embedding_model**: Embedding model to use (default: gemini)
    """
    try:
        collection = await collection_service.create(
            name=request.name,
            description=request.description,
            embedding_model=request.embedding_model,
            owner_id=user.id,
            db=db
        )
        return CollectionResponse.from_orm(collection)
    except CollectionExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Collection with this name already exists"
        )
```

### Dependency Injection
```python
# Database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Authentication dependency
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await user_service.get_by_id(user_id, db)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Permission dependency
def require_permission(permission: Permission):
    def permission_checker(user: User = Depends(get_current_user)) -> User:
        if not user.has_permission(permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return permission_checker
```

## Frontend Code Standards (TypeScript/React)

### Component Structure
```typescript
// Use functional components with TypeScript
interface ChatMessageProps {
  message: Message;
  onSourceClick: (source: Source) => void;
  isStreaming?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  onSourceClick,
  isStreaming = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const handleSourceClick = useCallback((source: Source) => {
    onSourceClick(source);
  }, [onSourceClick]);
  
  return (
    <div className="chat-message">
      <div className="message-content">
        {message.content}
      </div>
      {message.sources && (
        <SourcesList 
          sources={message.sources}
          onSourceClick={handleSourceClick}
        />
      )}
    </div>
  );
};
```

### State Management
```typescript
// Use Zustand for state management
interface ChatStore {
  messages: Message[];
  isLoading: boolean;
  currentSession: string | null;
  
  // Actions
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  startNewSession: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  isLoading: false,
  currentSession: null,
  
  addMessage: (message) => set((state) => ({
    messages: [...state.messages, message]
  })),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  startNewSession: () => set({
    currentSession: generateSessionId(),
    messages: []
  }),
  
  clearMessages: () => set({ messages: [] })
}));
```

### API Client
```typescript
// Centralized API client with error handling
class APIClient {
  private baseURL: string;
  private httpClient: AxiosInstance;
  
  constructor(baseURL: string) {
    this.baseURL = baseURL;
    this.httpClient = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor for auth
    this.httpClient.interceptors.request.use((config) => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
    
    // Response interceptor for error handling
    this.httpClient.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }
  
  async searchCollections(request: SearchRequest): Promise<SearchResult[]> {
    const response = await this.httpClient.post<SearchResult[]>(
      '/api/v1/search',
      request
    );
    return response.data;
  }
}
```

## Database Patterns

### SQLAlchemy Models
```python
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    embedding_model = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")
    owner = relationship("User", back_populates="collections")
    
    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, name='{self.name}')>"

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    collection_id = Column(UUID(as_uuid=True), ForeignKey("collections.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    collection = relationship("Collection", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
```

### Repository Pattern
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

class CollectionRepository(ABC):
    @abstractmethod
    async def create(self, collection: Collection) -> Collection:
        pass
    
    @abstractmethod
    async def get_by_id(self, collection_id: str) -> Optional[Collection]:
        pass
    
    @abstractmethod
    async def list_by_user(self, user_id: str) -> List[Collection]:
        pass

class SQLAlchemyCollectionRepository(CollectionRepository):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, collection: Collection) -> Collection:
        self.db.add(collection)
        await self.db.flush()
        await self.db.refresh(collection)
        return collection
    
    async def get_by_id(self, collection_id: str) -> Optional[Collection]:
        result = await self.db.execute(
            select(Collection).where(Collection.id == collection_id)
        )
        return result.scalar_one_or_none()
    
    async def list_by_user(self, user_id: str) -> List[Collection]:
        result = await self.db.execute(
            select(Collection)
            .where(Collection.owner_id == user_id)
            .order_by(Collection.created_at.desc())
        )
        return result.scalars().all()
```

## Testing Standards

### Unit Tests
```python
import pytest
from unittest.mock import AsyncMock, Mock
from advanced_rag_system.services.document_processor import DocumentProcessor

class TestDocumentProcessor:
    @pytest.fixture
    def mock_embedding_service(self):
        service = AsyncMock()
        service.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]
        return service
    
    @pytest.fixture
    def document_processor(self, mock_embedding_service):
        return DocumentProcessor(embedding_service=mock_embedding_service)
    
    @pytest.mark.asyncio
    async def test_process_document_success(self, document_processor):
        # Arrange
        document = Document(
            id="test-id",
            filename="test.pdf",
            content="Test content"
        )
        
        # Act
        result = await document_processor.process(document)
        
        # Assert
        assert result.status == "completed"
        assert len(result.chunks) > 0
        assert result.chunks[0].embedding is not None
    
    @pytest.mark.asyncio
    async def test_process_document_invalid_file(self, document_processor):
        # Arrange
        document = Document(
            id="test-id",
            filename="test.invalid",
            content=""
        )
        
        # Act & Assert
        with pytest.raises(UnsupportedFileTypeError):
            await document_processor.process(document)
```

### Integration Tests
```python
import pytest
from httpx import AsyncClient
from advanced_rag_system.main import app

@pytest.mark.asyncio
async def test_create_collection_integration():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create test user and get auth token
        auth_response = await client.post("/auth/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        token = auth_response.json()["access_token"]
        
        # Create collection
        response = await client.post(
            "/api/v1/collections/",
            json={
                "name": "Test Collection",
                "description": "A test collection",
                "embedding_model": "gemini"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Collection"
        assert "id" in data
```

## Logging Standards

### Structured Logging
```python
import structlog
from typing import Any, Dict

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Usage examples
async def process_document(document_id: str) -> None:
    log = logger.bind(document_id=document_id, operation="process_document")
    
    log.info("Starting document processing")
    
    try:
        result = await _extract_text(document_id)
        log.info("Document processing completed", 
                chunks_created=len(result.chunks),
                processing_time=result.processing_time)
    except Exception as e:
        log.error("Document processing failed", 
                 error=str(e),
                 error_type=type(e).__name__)
        raise
```

## Security Guidelines

### Input Validation
```python
from pydantic import BaseModel, validator, Field
from typing import List

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    collection_ids: List[str] = Field(..., min_items=1, max_items=10)
    limit: int = Field(10, ge=1, le=100)
    
    @validator('query')
    def validate_query(cls, v):
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&']
        for char in dangerous_chars:
            if char in v:
                raise ValueError(f"Query contains invalid character: {char}")
        return v.strip()
    
    @validator('collection_ids')
    def validate_collection_ids(cls, v):
        # Validate UUID format
        for collection_id in v:
            try:
                uuid.UUID(collection_id)
            except ValueError:
                raise ValueError(f"Invalid collection ID format: {collection_id}")
        return v
```

### SQL Injection Prevention
```python
# Always use parameterized queries
async def get_documents_by_collection(
    collection_id: str,
    db: AsyncSession
) -> List[Document]:
    # Good - parameterized query
    result = await db.execute(
        select(Document).where(Document.collection_id == collection_id)
    )
    return result.scalars().all()

# Never use string formatting for SQL
# Bad example (DO NOT DO THIS):
# query = f"SELECT * FROM documents WHERE collection_id = '{collection_id}'"
```

---
*Last Updated: Current Session*
*Next Update: As coding standards evolve and new patterns are adopted* 