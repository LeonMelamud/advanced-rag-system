# Technology Context

## Technology Stack Overview

### Backend Services
- **Framework**: FastAPI (Python 3.11+)
- **Async Runtime**: asyncio with uvloop
- **API Documentation**: OpenAPI/Swagger auto-generation
- **Validation**: Pydantic v2 for data validation and serialization
- **HTTP Client**: httpx for async HTTP requests

### Frontend Application
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **State Management**: Zustand or Redux Toolkit (TBD based on complexity)
- **UI Components**: Custom components with Tailwind CSS
- **HTTP Client**: Axios or fetch API with React Query for caching

### Databases & Storage

#### Vector Databases
- **Primary**: Qdrant (open-source, self-hosted)
- **Alternative**: Pinecone (managed service option)
- **Backup Option**: Weaviate (for specific use cases)
- **Rationale**: Qdrant provides excellent performance, open-source flexibility, and comprehensive metadata filtering

#### Relational Database
- **Primary**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 with async support
- **Migrations**: Alembic for database schema management
- **Connection Pooling**: asyncpg with SQLAlchemy async engine

#### Caching & Message Queue
- **Cache**: Redis 7+ for session storage, query caching, and distributed locks
- **Message Queue**: Redis Streams or RabbitMQ for async processing
- **Rationale**: Redis provides both caching and lightweight message queue capabilities

#### File Storage
- **Development**: Local filesystem with organized directory structure
- **Production**: S3-compatible storage (AWS S3, MinIO, or similar)
- **CDN**: CloudFront or similar for static asset delivery

### AI/ML Services

#### Large Language Models
- **Primary**: Google Gemini 2.0 Flash (latest, optimized for speed and performance)
- **Complex Tasks**: Google Gemini 1.5 Pro (for complex reasoning and long context)
- **Fallback**: OpenAI GPT-4o (proven reliability, industry standard)
- **Cost-Effective**: OpenAI GPT-4o-mini (for simple tasks and high-volume operations)
- **Local Option**: Ollama for on-premise deployments (development/testing)

#### LLM Selection Strategy for RAG
```python
# Model Selection by Use Case:
RAG_MODELS = {
    "primary_generation": {
        "model": "gemini-2.0-flash",
        "provider": "google",
        "use_case": "Main RAG responses, fast generation",
        "context_window": "1M tokens",
        "cost": "Low",
        "speed": "Very Fast"
    },
    "complex_reasoning": {
        "model": "gemini-1.5-pro", 
        "provider": "google",
        "use_case": "Complex queries, long documents",
        "context_window": "2M tokens", 
        "cost": "Medium",
        "speed": "Medium"
    },
    "fallback_primary": {
        "model": "gpt-4o",
        "provider": "openai", 
        "use_case": "Fallback, evaluation, comparison",
        "context_window": "128K tokens",
        "cost": "High",
        "speed": "Fast"
    },
    "fallback_cost_effective": {
        "model": "gpt-4o-mini",
        "provider": "openai",
        "use_case": "Simple queries, high volume",
        "context_window": "128K tokens", 
        "cost": "Very Low",
        "speed": "Very Fast"
    }
}
```

#### Embedding Models
- **Primary**: Google text-embedding-004 (latest Gemini-based, MTEB leaderboard top performer)
- **Fallback**: OpenAI text-embedding-3-small (fast, cost-effective, 1536 dimensions)
- **Local Option**: Sentence Transformers for offline/specialized applications
- **Rationale**: text-embedding-3-large too slow for production, 3-small provides good balance

#### Embedding Model Selection Strategy
```python
# Embedding Model Configuration:
EMBEDDING_MODELS = {
    "primary": {
        "model": "text-embedding-004",
        "provider": "google",
        "dimensions": 768,
        "max_tokens": 2048,
        "cost": "Low",
        "performance": "MTEB #1 Multilingual",
        "speed": "Fast",
        "use_case": "Main embedding for all documents"
    },
    "fallback": {
        "model": "text-embedding-3-small", 
        "provider": "openai",
        "dimensions": 1536,
        "max_tokens": 8191,
        "cost": "Low",
        "performance": "Good",
        "speed": "Very Fast",
        "use_case": "Fallback and high-volume operations"
    },
    "local": {
        "model": "all-MiniLM-L6-v2",
        "provider": "sentence-transformers", 
        "dimensions": 384,
        "max_tokens": 256,
        "cost": "Free",
        "performance": "Good for general use",
        "speed": "Very Fast",
        "use_case": "Offline, development, specialized domains"
    }
}
```

#### Retrieval Strategy Configuration

**Top-K Retrieval with Hybrid Approach**:
```python
# Retrieval Configuration:
RETRIEVAL_CONFIG = {
    "primary_strategy": "hybrid_search",
    "vector_search": {
        "top_k": 20,  # Initial broad retrieval
        "similarity_threshold": 0.7,
        "algorithm": "cosine_similarity"
    },
    "keyword_search": {
        "top_k": 10,
        "algorithm": "BM25",
        "boost_factor": 0.3
    },
    "reranking": {
        "enabled": True,
        "final_k": 5,  # Final context chunks
        "method": "cross_encoder",
        "model": "ms-marco-MiniLM-L-6-v2"
    },
    "context_window": {
        "max_tokens": 4000,  # For Gemini context
        "overlap_strategy": "smart_merge"
    }
}
```

**Advanced Retrieval Strategies**:
```python
# Multi-Stage Retrieval Pipeline:
RETRIEVAL_PIPELINE = {
    "stage_1_broad_search": {
        "method": "vector_similarity",
        "top_k": 50,
        "threshold": 0.6,
        "purpose": "Cast wide net"
    },
    "stage_2_keyword_boost": {
        "method": "bm25_hybrid", 
        "top_k": 20,
        "weight": 0.3,
        "purpose": "Boost exact matches"
    },
    "stage_3_reranking": {
        "method": "cross_encoder",
        "top_k": 10,
        "model": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "purpose": "Semantic reranking"
    },
    "stage_4_context_selection": {
        "method": "mmr",  # Maximal Marginal Relevance
        "final_k": 5,
        "diversity_factor": 0.3,
        "purpose": "Diverse, relevant context"
    }
}
```

#### Chunking Strategy Configuration

**Research-Based Best Practices (2024)**:
```python
# Optimal Chunking Configuration Based on Latest Research:
CHUNKING_CONFIG = {
    "strategy": "semantic_hybrid",  # Best performing according to 2024 studies
    "base_chunk_size": 512,  # Optimal balance for most use cases
    "max_chunk_size": 1024,  # For complex context preservation
    "min_chunk_size": 256,   # For granular fact-based queries
    "overlap_size": 128,     # 25% overlap (research-proven optimal)
    "overlap_strategy": "sentence_boundary",
    
    # Query-type adaptive chunking
    "adaptive_sizing": {
        "fact_based_queries": 256,    # Smaller for precise keyword matching
        "conceptual_queries": 512,    # Balanced for general understanding
        "complex_analysis": 1024,     # Larger for broader context
        "summarization": 768          # Medium-large for comprehensive coverage
    }
}
```

**Advanced Chunking Methods (2024 Best Practices)**:
```python
# Hierarchical Chunking Strategies:
ADVANCED_CHUNKING = {
    "semantic_chunking": {
        "description": "Split based on semantic similarity between sentences",
        "algorithm": "sentence_transformers_similarity",
        "threshold": 0.8,
        "advantages": ["Coherent information", "Context preservation", "Best performance"],
        "use_case": "Primary strategy for most documents",
        "research_finding": "Outperforms all other strategies in 2024 studies"
    },
    
    "agentic_chunking": {
        "description": "AI agent decides chunk boundaries based on content",
        "algorithm": "llm_guided_splitting",
        "model": "gpt-4o-mini",  # Cost-effective for chunking decisions
        "advantages": ["Intelligent boundaries", "Content-aware", "Adaptive"],
        "use_case": "High-value documents requiring optimal chunking",
        "cost": "Higher but justified for critical content"
    },
    
    "late_chunking": {
        "description": "Embed full document, then chunk embeddings",
        "algorithm": "post_embedding_segmentation",
        "advantages": ["Global context", "Better embeddings", "Reduced information loss"],
        "use_case": "Documents where global context is crucial",
        "research_finding": "Emerging technique showing promise"
    },
    
    "recursive_character": {
        "description": "LangChain's hierarchical splitting approach",
        "separators": ["\n\n", "\n", ". ", "! ", "? ", " "],
        "advantages": ["Reliable", "Respects structure", "Well-tested"],
        "use_case": "Fallback strategy, general purpose",
        "research_finding": "Solid baseline, but semantic chunking performs better"
    }
}
```

**Document-Type Optimized Chunking**:
```python
# Research-Based Document Strategies:
DOCUMENT_STRATEGIES = {
    "pdf_academic": {
        "method": "semantic_sectioning",
        "chunk_size": 768,  # Larger for academic context
        "overlap": 192,     # 25% overlap
        "respect_headers": True,
        "preserve_citations": True,
        "research_basis": "Academic papers need larger context windows"
    },
    
    "pdf_technical": {
        "method": "hybrid_semantic_structure",
        "chunk_size": 512,
        "overlap": 128,
        "respect_code_blocks": True,
        "preserve_diagrams": True,
        "research_basis": "Technical docs benefit from structure preservation"
    },
    
    "markdown_documentation": {
        "method": "header_based_semantic",
        "chunk_size": 512,
        "overlap": 128,
        "respect_structure": True,
        "preserve_code_examples": True,
        "research_basis": "Documentation structure is semantically meaningful"
    },
    
    "conversational_text": {
        "method": "dialogue_aware",
        "chunk_size": 256,  # Smaller for conversational context
        "overlap": 64,
        "preserve_speaker_turns": True,
        "research_basis": "Conversations need speaker context preservation"
    },
    
    "legal_documents": {
        "method": "clause_based_semantic",
        "chunk_size": 1024,  # Larger for legal context
        "overlap": 256,      # Higher overlap for legal precision
        "preserve_numbering": True,
        "research_basis": "Legal text requires extensive context"
    }
}
```

**Overlap Strategy Optimization**:
```python
# Research-Proven Overlap Strategies:
OVERLAP_STRATEGIES = {
    "percentage_based": {
        "optimal_percentage": 25,  # 25% overlap proven optimal in studies
        "min_percentage": 10,      # Minimum for context preservation
        "max_percentage": 50,      # Maximum before diminishing returns
        "research_finding": "25% overlap provides best balance of context vs redundancy"
    },
    
    "sentence_boundary": {
        "description": "Overlap at complete sentences only",
        "advantages": ["Maintains semantic integrity", "No broken sentences"],
        "implementation": "spacy_sentence_segmentation",
        "research_finding": "Prevents context fragmentation"
    },
    
    "sliding_window": {
        "description": "Fixed-size overlapping windows",
        "window_size": 512,
        "step_size": 384,  # 75% step = 25% overlap
        "use_case": "Dense technical documents",
        "research_finding": "Good for information-dense content"
    }
}
```

**Performance-Based Chunk Size Selection**:
```python
# Empirical Chunk Size Research Results:
CHUNK_SIZE_RESEARCH = {
    "embedding_model_optimization": {
        "text_embedding_004": {
            "optimal_size": 512,
            "range": "256-768",
            "research_finding": "Google embeddings perform best at 512 tokens"
        },
        "text_embedding_3_small": {
            "optimal_size": 512,
            "range": "256-1024", 
            "research_finding": "OpenAI embeddings stable across range, 512 optimal"
        }
    },
    
    "query_type_optimization": {
        "fact_retrieval": {
            "optimal_size": 256,
            "reason": "Precise keyword matching, minimal noise"
        },
        "conceptual_understanding": {
            "optimal_size": 512,
            "reason": "Balance of context and specificity"
        },
        "complex_reasoning": {
            "optimal_size": 1024,
            "reason": "Requires broader context for understanding"
        },
        "summarization": {
            "optimal_size": 768,
            "reason": "Comprehensive coverage without overwhelming detail"
        }
    }
}
```

#### Context Merging and Selection

**Smart Context Assembly**:
```python
# Context Assembly Strategy:
CONTEXT_ASSEMBLY = {
    "max_context_tokens": 4000,  # For Gemini models
    "assembly_method": "relevance_weighted",
    "strategies": {
        "simple_concatenation": {
            "method": "join_by_relevance",
            "separator": "\n\n---\n\n",
            "use_case": "Basic RAG"
        },
        "weighted_selection": {
            "method": "score_based_selection",
            "weights": {
                "similarity_score": 0.4,
                "keyword_match": 0.3,
                "recency": 0.2,
                "source_authority": 0.1
            },
            "use_case": "Advanced RAG with quality signals"
        },
        "mmr_diversification": {
            "method": "maximal_marginal_relevance",
            "lambda_param": 0.7,  # Relevance vs diversity balance
            "use_case": "Avoid redundant information"
        }
    }
}
```

#### Model Performance Rationale

**Gemini 2.0 Flash for RAG**:
- Latest Google model optimized for speed and performance
- Native tool use capabilities for agentic workflows
- Lower cost than Gemini 1.5 Flash with better performance
- Excellent for production RAG applications

**Gemini 1.5 Pro for Complex Tasks**:
- 2M token context window for very long documents
- Superior performance on complex reasoning tasks
- Better for multi-document synthesis
- Ideal for complex queries requiring deep analysis

**GPT-4o as Fallback**:
- Industry standard reliability and consistency
- Excellent for evaluation and comparison
- Proven performance across diverse tasks
- Strong reasoning capabilities

**text-embedding-004 Primary Choice**:
- Top performer on MTEB multilingual leaderboard
- Trained on Gemini model for consistency
- Lower cost than OpenAI alternatives
- Excellent semantic understanding

#### Document Processing
- **PDF**: PyMuPDF (fitz) for text extraction and metadata
- **Audio**: OpenAI Whisper for transcription
- **CSV**: pandas for structured data processing
- **Text**: Built-in Python text processing with encoding detection

#### LLM Framework Selection
- **Primary**: LangGraph for agent orchestration and complex workflows
- **Secondary**: LangChain for basic RAG components and utilities
- **Rationale**: 
  - **LangGraph**: Community consensus for production agents in 2024, better control and state management
  - **LangChain**: Still valuable for basic RAG utilities and integrations
  - **Decision**: LangGraph for main orchestration, LangChain components as building blocks

#### Framework Architecture Strategy
```python
# LangGraph + LangChain Hybrid Approach:
1. LangGraph - Main agent orchestration and workflow control
2. LangChain - Utility components (document loaders, text splitters, etc.)
3. Direct API calls - For simple LLM interactions where frameworks add overhead
4. Custom components - For specialized RAG logic
```

#### Why LangGraph Over Pure LangChain (2024 Community Consensus):
- **Production Ready**: Major companies (LinkedIn, Uber, Replit, Elastic) using in production
- **Better Control**: More controllable agents with custom cognitive architectures
- **State Management**: Built-in state management for complex workflows
- **Debugging**: Visual studio for debugging agent workflows
- **Cyclical Graphs**: Better support for agent loops and decision trees
- **Performance**: Lower-level control for optimization

### LLM Observability & Monitoring

#### Primary Observability Platform
- **Primary**: Langfuse (open-source, self-hosted)
- **Alternative**: Weights & Biases (W&B) for ML experiment tracking
- **Backup**: Arize Phoenix for real-time monitoring
- **Rationale**: Langfuse provides comprehensive LLM observability with self-hosting control

#### Observability Stack
```python
# Core Observability Components:
1. Langfuse - LLM tracing, prompt management, evaluation
2. OpenTelemetry - Distributed tracing standard
3. Prometheus + Grafana - Infrastructure metrics
4. Custom metrics - Business-specific KPIs
```

#### Key Metrics to Track
```yaml
# LLM Performance Metrics:
- Response latency (P50, P95, P99)
- Token usage (input/output tokens)
- Cost per request
- Error rates and failure modes
- Model accuracy and quality scores

# Business Metrics:
- User satisfaction ratings
- Query success rate
- Source attribution accuracy
- Response relevance scores
```

### LLM Evaluation Framework

#### LLM-as-a-Judge Implementation
- **Primary Judge Model**: GPT-4 or Gemini Pro for evaluation
- **Evaluation Dimensions**:
  - **Relevance**: How well the response answers the question
  - **Accuracy**: Factual correctness of the information
  - **Completeness**: Whether the response covers all aspects
  - **Source Attribution**: Proper citation of source documents
  - **Hallucination Detection**: Identifying fabricated information

#### Evaluation Metrics & Approaches
```python
# Automated Evaluation Metrics:
1. RAGAS (RAG Assessment) - Comprehensive RAG evaluation
2. Context Relevance - Retrieved context quality
3. Answer Relevance - Response quality assessment
4. Faithfulness - Groundedness to source material
5. Custom LLM-as-Judge evaluators

# Traditional Metrics:
- BLEU/ROUGE scores for text similarity
- Semantic similarity using embeddings
- Retrieval metrics (MRR, NDCG, Hit Rate)
```

#### Evaluation Pipeline
```python
# Multi-Stage Evaluation Process:
1. Retrieval Evaluation - Quality of retrieved documents
2. Generation Evaluation - Quality of generated responses
3. End-to-End Evaluation - Overall system performance
4. Human Evaluation - Periodic human validation
5. A/B Testing - Comparative model performance
```

### Evaluation Tools & Frameworks

#### Primary Evaluation Stack
- **LLM-as-Judge**: GPT-4/Gemini for automated evaluation
- **RAGAS**: Specialized RAG evaluation framework
- **Phoenix Evals**: Real-time evaluation capabilities
- **Custom Evaluators**: Domain-specific evaluation logic

#### Evaluation Configuration
```python
# LLM-as-Judge Setup:
EVALUATION_CONFIG = {
    "judge_model": "gpt-4",
    "evaluation_criteria": {
        "relevance": {"weight": 0.3, "threshold": 0.7},
        "accuracy": {"weight": 0.3, "threshold": 0.8},
        "completeness": {"weight": 0.2, "threshold": 0.6},
        "attribution": {"weight": 0.2, "threshold": 0.9}
    },
    "consensus_voting": True,  # Use multiple judges for critical evaluations
    "explanation_required": True  # Require reasoning for scores
}
```

#### Golden Dataset Strategy
```python
# Evaluation Dataset Management:
1. Curated golden questions with expert answers
2. Domain-specific test cases
3. Edge case scenarios
4. Adversarial examples for robustness testing
5. Regular dataset updates and validation
```

### Infrastructure & Deployment

#### Containerization
- **Runtime**: Docker with multi-stage builds
- **Orchestration**: Kubernetes for production, Docker Compose for development
- **Registry**: Docker Hub or private registry (AWS ECR, Google GCR)

#### API Gateway
- **Development**: Nginx or Traefik for simple routing
- **Production**: Kong, Ambassador, or cloud-native solutions
- **Features**: Rate limiting, authentication, load balancing, SSL termination

#### Monitoring & Observability
- **Metrics**: Prometheus with Grafana dashboards
- **Logging**: Structured logging with ELK stack (Elasticsearch, Logstash, Kibana)
- **Tracing**: OpenTelemetry with Jaeger for distributed tracing
- **Health Checks**: Custom health endpoints with dependency checks

#### Security
- **Authentication**: JWT tokens with RS256 signing
- **Authorization**: Role-Based Access Control (RBAC)
- **Secrets Management**: HashiCorp Vault or Kubernetes secrets
- **TLS**: Let's Encrypt certificates with automatic renewal

## Development Tools & Practices

### Package Management
- **Python**: uv for fast dependency resolution and virtual environment management
- **Node.js**: npm or yarn for frontend dependencies
- **Rationale**: uv provides significantly faster dependency resolution than pip

### Code Quality
- **Linting**: 
  - Python: ruff (replaces flake8, black, isort)
  - TypeScript: ESLint with TypeScript rules
- **Formatting**: 
  - Python: ruff format (black-compatible)
  - TypeScript: Prettier
- **Type Checking**: 
  - Python: mypy for static type checking
  - TypeScript: Built-in TypeScript compiler

### Testing
- **Python**: pytest with async support, pytest-cov for coverage
- **Frontend**: Jest and React Testing Library for unit tests
- **Integration**: pytest with testcontainers for database testing
- **E2E**: Playwright for end-to-end testing

### Version Control & CI/CD
- **VCS**: Git with conventional commit messages
- **CI/CD**: GitHub Actions or GitLab CI
- **Deployment**: GitOps with ArgoCD for Kubernetes deployments
- **Environments**: Development, Staging, Production with environment-specific configurations

## Technology Decisions & Rationale

### 1. FastAPI vs Django/Flask
**Decision**: FastAPI
**Rationale**:
- Native async support for better performance
- Automatic OpenAPI documentation generation
- Excellent type hints integration with Pydantic
- Modern Python features and best practices
- Better performance for I/O-bound operations (AI API calls)

### 2. Microservices vs Monolith
**Decision**: Microservices Architecture
**Rationale**:
- Independent scaling of different components (file processing vs chat)
- Technology diversity (different services can use optimal tech stacks)
- Team autonomy and parallel development
- Fault isolation and resilience
- Better resource utilization

### 3. Qdrant vs Pinecone vs Weaviate
**Decision**: Qdrant as primary, Pinecone as alternative
**Rationale**:
- **Qdrant**: Open-source, excellent performance, rich metadata filtering, self-hosted control
- **Pinecone**: Managed service option for easier operations, good performance
- **Weaviate**: Good for specific use cases but more complex setup

### 4. PostgreSQL vs MongoDB
**Decision**: PostgreSQL
**Rationale**:
- ACID compliance for critical metadata
- Excellent JSON support for flexible schemas
- Strong ecosystem and tooling
- Better integration with Python ORM tools
- Proven scalability and reliability

### 5. React vs Vue vs Angular
**Decision**: React with TypeScript
**Rationale**:
- Large ecosystem and community
- Excellent TypeScript support
- Flexible architecture for complex UIs
- Strong tooling and development experience
- Team familiarity and hiring considerations

## Performance Considerations

### Database Optimization
```sql
-- Indexes for common query patterns
CREATE INDEX idx_documents_collection_id ON documents(collection_id);
CREATE INDEX idx_documents_created_at ON documents(created_at);
CREATE INDEX idx_chunks_document_id ON chunks(document_id);
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);

-- Partial indexes for active records
CREATE INDEX idx_active_documents ON documents(id) WHERE status = 'active';
```

### Caching Strategy
```python
# Multi-level caching configuration
CACHE_CONFIG = {
    "query_results": {"ttl": 300, "max_size": 1000},  # 5 minutes
    "embeddings": {"ttl": 3600, "max_size": 10000},   # 1 hour
    "user_sessions": {"ttl": 1800, "max_size": 5000}, # 30 minutes
    "collection_metadata": {"ttl": 7200, "max_size": 500}  # 2 hours
}
```

### Connection Pooling
```python
# Database connection pool settings
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": False  # Set to True for SQL debugging
}

# HTTP client configuration
HTTP_CLIENT_CONFIG = {
    "timeout": 30.0,
    "max_keepalive_connections": 20,
    "max_connections": 100,
    "retries": 3
}
```

## Security Configuration

### JWT Configuration
```python
JWT_CONFIG = {
    "algorithm": "RS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
    "issuer": "advanced-rag-system",
    "audience": "rag-api"
}
```

### CORS Configuration
```python
CORS_CONFIG = {
    "allow_origins": ["http://localhost:3000"],  # Frontend URL
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Request-ID"]
}
```

### Rate Limiting
```python
RATE_LIMIT_CONFIG = {
    "chat_queries": "10/minute",
    "file_uploads": "5/minute", 
    "collection_operations": "20/minute",
    "search_queries": "30/minute"
}
```

## Environment Configuration

### Development Environment
```yaml
# config/development.yaml
database:
  url: "postgresql+asyncpg://user:pass@localhost:5432/rag_dev"
  echo: true

redis:
  url: "redis://localhost:6379/0"

vector_db:
  type: "qdrant"
  url: "http://localhost:6333"

ai_services:
  gemini_api_key: "${GEMINI_API_KEY}"
  openai_api_key: "${OPENAI_API_KEY}"

logging:
  level: "DEBUG"
  format: "detailed"
```

### Production Environment
```yaml
# config/production.yaml
database:
  url: "${DATABASE_URL}"
  echo: false
  pool_size: 20

redis:
  url: "${REDIS_URL}"
  ssl_cert_reqs: "required"

vector_db:
  type: "qdrant"
  url: "${QDRANT_URL}"
  api_key: "${QDRANT_API_KEY}"

ai_services:
  gemini_api_key: "${GEMINI_API_KEY}"
  rate_limit: "1000/hour"

logging:
  level: "INFO"
  format: "json"

security:
  cors_origins: ["https://app.example.com"]
  jwt_secret_key: "${JWT_SECRET_KEY}"
```

## Migration & Upgrade Strategy

### Database Migrations
- Use Alembic for PostgreSQL schema changes
- Version-controlled migration scripts
- Automated migration testing in CI/CD
- Rollback procedures for failed migrations

### Vector Database Migrations
- Collection versioning for schema changes
- Gradual migration for embedding model updates
- Backup and restore procedures
- Zero-downtime migration strategies

### Service Updates
- Blue-green deployments for zero downtime
- Feature flags for gradual rollouts
- Automated rollback on health check failures
- Database migration coordination with service updates

## Monitoring & Alerting

### Key Metrics
- **Performance**: Response times, throughput, error rates
- **Business**: Query accuracy, user satisfaction, usage patterns
- **Infrastructure**: CPU, memory, disk usage, network latency
- **AI Services**: Token usage, model performance, API quotas

### Alert Thresholds
```yaml
alerts:
  response_time_p95: "> 3s"
  error_rate: "> 1%"
  database_connections: "> 80%"
  vector_db_latency: "> 1s"
  ai_api_quota: "> 90%"
  disk_usage: "> 85%"
```

#### LangGraph + Multi-Model Integration
```python
# LangGraph with Multi-Provider Configuration:
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

# Primary Gemini models
gemini_flash = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

gemini_pro = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", 
    temperature=0.1,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# OpenAI fallback models
openai_gpt4o = ChatOpenAI(
    model="gpt-4o",
    temperature=0.1,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

openai_gpt4o_mini = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1, 
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Model selection logic
def select_model(task_type: str, complexity: str):
    if task_type == "rag_generation":
        return gemini_flash if complexity == "simple" else gemini_pro
    elif task_type == "fallback":
        return openai_gpt4o if complexity == "complex" else openai_gpt4o_mini
```

---
*Last Updated: Current Session*
*Next Update: As technology decisions evolve and new tools are evaluated* 