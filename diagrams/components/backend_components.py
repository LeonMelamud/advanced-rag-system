#!/usr/bin/env python3
"""
Advanced RAG System - Backend Components (Updated)
Shows the actual implemented structure and relationships of FastAPI microservices
Reflects the fully operational RAG system with working authentication, file processing, and chat service
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.ml import SagemakerModel
from diagrams.gcp.ml import AutoML
from diagrams.generic.compute import Rack
from diagrams.generic.storage import Storage
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Memcached, Redis
from diagrams.onprem.monitoring import Grafana
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python

# Component colors
COLORS = {
    "api": "#3498db",  # Blue
    "business": "#2ecc71",  # Green
    "data": "#e74c3c",  # Red
    "shared": "#9b59b6",  # Purple
    "middleware": "#f39c12",  # Orange
    "ai": "#1abc9c",  # Teal
    "external": "#95a5a6",  # Gray
}

with Diagram(
    "Advanced RAG System - Backend Components (Operational)",
    filename=str(Path(__file__).parent.parent / "generated" / "backend_components"),
    show=False,
    direction="TB",
    graph_attr={"fontsize": "18", "bgcolor": "white"},
):

    # API Gateway & Load Balancing
    with Cluster("API Gateway & Load Balancing"):
        gateway = Nginx("API Gateway\n(Nginx)")
        rate_limiter = Rack("Rate Limiter\n(Implemented)")
        auth_middleware = Rack("JWT Middleware\n(Working)")

    # Shared Components (DRY Architecture)
    with Cluster("Shared Components (backend/common/) - DRY Architecture"):
        with Cluster("Core Shared Services"):
            service_factory = Python("Service Factory\n(DRY Pattern)")
            shared_auth = Python("JWT Auth Utils\n(Working)")
            shared_config = Python("Config Manager\n(YAML + Env)")
            shared_health = Python("Health Checks\n(All Services)")

        with Cluster("Database & Vector Services"):
            shared_db = Python("Database Utils\n(SQLAlchemy)")
            vector_service = Python("Vector Service\n(Qdrant Client)")
            shared_models = Python("Database Models\n(Complete Schema)")

        with Cluster("Utilities"):
            shared_schemas = Python("Pydantic Schemas\n(Validation)")
            shared_utils = Python("Common Utils\n(Helpers)")
            shared_exceptions = Python("Exception Handling\n(Standardized)")

    # Auth Service (Fully Implemented)
    with Cluster("Auth Service (✅ OPERATIONAL)"):
        with Cluster("API Layer"):
            auth_router = FastAPI("Auth Router\n(/api/v1/auth/*)")
            user_router = FastAPI("User Router\n(/api/v1/users/*)")

        with Cluster("Business Logic"):
            auth_service = Python("Auth Service\n(JWT + RBAC)")
            user_service = Python("User Service\n(CRUD Operations)")
            password_service = Python("Password Service\n(bcrypt Hashing)")
            token_service = Python("Token Service\n(Refresh Logic)")

        with Cluster("Data Layer"):
            user_crud = Python("User CRUD\n(Async SQLAlchemy)")
            session_manager = Python("Session Manager\n(Redis Cache)")

    # File Service (Fully Implemented)
    with Cluster("File Service (✅ OPERATIONAL)"):
        with Cluster("API Layer"):
            upload_router = FastAPI("Upload Router\n(/api/v1/files/upload)")
            files_router = FastAPI("Files Router\n(/api/v1/files/*)")
            vector_router = FastAPI("Vector Router\n(/api/v1/files/vector/*)")
            search_router = FastAPI("Search Router\n(/api/v1/files/search/*)")

        with Cluster("Processing Pipeline"):
            file_processor = Python("File Processor\n(Multi-format)")
            text_extractor = Python("Text Extractor\n(PyMuPDF, pandas)")
            chunking_service = Python("Chunking Service\n(4 Strategies)")
            embedding_service = Python("Embedding Service\n(OpenAI API)")

        with Cluster("Data & Storage"):
            file_crud = Python("File CRUD\n(Metadata)")
            file_storage = Storage("File Storage\n(Local/S3)")
            vector_manager = Python("Vector Manager\n(Qdrant)")

    # Chat Service (Fully Implemented RAG)
    with Cluster("Chat Service (✅ RAG OPERATIONAL)"):
        with Cluster("API Layer"):
            chat_router = FastAPI("Chat Router\n(/api/v1/chat/*)")
            sessions_router = FastAPI("Sessions Router\n(/api/v1/sessions/*)")

        with Cluster("RAG Pipeline"):
            rag_service = Python("RAG Service\n(Complete Pipeline)")
            query_processor = Python("Query Processor\n(Preprocessing)")
            retrieval_service = Python("Retrieval Service\n(Vector + BM25)")
            context_merger = Python("Context Merger\n(Enhanced RRF)")
            llm_service = Python("LLM Service\n(OpenAI GPT-4)")

        with Cluster("Data Management"):
            chat_crud = Python("Chat CRUD\n(Sessions + Messages)")
            message_crud = Python("Message CRUD\n(Enum Fixed)")
            cache_manager = Python("Cache Manager\n(Redis)")

    # Collection Service (Basic Structure)
    with Cluster("Collection Service (Basic Structure)"):
        with Cluster("API Layer"):
            collection_router = FastAPI("Collection Router\n(/api/v1/collections/*)")
            document_router = FastAPI("Document Router\n(/api/v1/documents/*)")

        with Cluster("Business Logic"):
            collection_service = Python("Collection Service\n(Basic CRUD)")
            document_service = Python("Document Service\n(Management)")

        with Cluster("Data Layer"):
            collection_crud = Python("Collection CRUD\n(Basic)")

    # MCP Orchestrator (Future Enhancement)
    with Cluster("MCP Orchestrator (Future Enhancement)"):
        mcp_router = FastAPI("MCP Router\n(/api/v1/mcp/*)")
        tool_service = Python("Tool Service\n(Placeholder)")

    # Data Stores (All Operational)
    with Cluster("Data Stores (✅ ALL OPERATIONAL)"):
        postgres = PostgreSQL("PostgreSQL\n(Primary DB)")
        redis = Redis("Redis\n(Cache + Sessions)")
        qdrant = Memcached("Qdrant\n(Vector DB)")

    # External AI Services (Working)
    with Cluster("External AI Services (✅ WORKING)"):
        openai_llm = SagemakerModel("OpenAI GPT-4\n(Chat Completion)")
        openai_embed = SagemakerModel("OpenAI Embeddings\n(text-embedding-3-small)")
        gemini_llm = AutoML("Google Gemini\n(Alternative)")

    # Monitoring & Observability
    with Cluster("Monitoring & Observability"):
        langfuse = Grafana("Langfuse\n(LLM Observability)")
        prometheus = Grafana("Prometheus\n(Metrics)")
        health_monitor = Rack("Health Monitor\n(All Services)")

    # API Gateway Flow
    gateway >> Edge(color=COLORS["middleware"], label="Rate Limit") >> rate_limiter
    rate_limiter >> Edge(color=COLORS["middleware"], label="JWT Auth") >> auth_middleware

    # Gateway to Services
    (
        auth_middleware
        >> Edge(color=COLORS["api"], label="Route")
        >> [auth_router, upload_router, chat_router, collection_router]
    )

    # Shared Components Usage (DRY Pattern)
    (
        service_factory
        >> Edge(color=COLORS["shared"], style="dashed", label="Creates")
        >> [auth_service, file_processor, rag_service, collection_service]
    )
    (
        shared_auth
        >> Edge(color=COLORS["shared"], style="dashed", label="JWT")
        >> [auth_service, file_processor, rag_service]
    )
    (
        shared_config
        >> Edge(color=COLORS["shared"], style="dashed", label="Config")
        >> [auth_service, file_processor, rag_service, collection_service]
    )
    (
        shared_db
        >> Edge(color=COLORS["shared"], style="dashed", label="DB Utils")
        >> [user_crud, file_crud, chat_crud, collection_crud]
    )
    (
        vector_service
        >> Edge(color=COLORS["shared"], style="dashed", label="Vector Ops")
        >> [vector_manager, retrieval_service]
    )
    (
        shared_models
        >> Edge(color=COLORS["shared"], style="dashed", label="Models")
        >> [user_crud, file_crud, chat_crud]
    )

    # Auth Service Flow (Working)
    auth_router >> Edge(color=COLORS["business"], label="Login/Register") >> auth_service
    user_router >> Edge(color=COLORS["business"], label="Profile") >> user_service
    auth_service >> Edge(color=COLORS["business"], label="Hash") >> password_service
    auth_service >> Edge(color=COLORS["business"], label="JWT") >> token_service
    [auth_service, user_service] >> Edge(color=COLORS["data"], label="CRUD") >> user_crud
    token_service >> Edge(color=COLORS["data"], label="Cache") >> session_manager

    # File Service Flow (Working)
    upload_router >> Edge(color=COLORS["business"], label="Upload") >> file_processor
    files_router >> Edge(color=COLORS["business"], label="Manage") >> file_processor
    file_processor >> Edge(color=COLORS["business"], label="Extract") >> text_extractor
    text_extractor >> Edge(color=COLORS["business"], label="Chunk") >> chunking_service
    chunking_service >> Edge(color=COLORS["ai"], label="Embed") >> embedding_service
    file_processor >> Edge(color=COLORS["data"], label="Metadata") >> file_crud
    file_processor >> Edge(color=COLORS["data"], label="Store") >> file_storage
    embedding_service >> Edge(color=COLORS["data"], label="Vectors") >> vector_manager

    # Chat Service RAG Flow (Working)
    chat_router >> Edge(color=COLORS["business"], label="Message") >> rag_service
    rag_service >> Edge(color=COLORS["business"], label="Process") >> query_processor
    query_processor >> Edge(color=COLORS["business"], label="Retrieve") >> retrieval_service
    retrieval_service >> Edge(color=COLORS["business"], label="Merge") >> context_merger
    context_merger >> Edge(color=COLORS["ai"], label="Generate") >> llm_service
    rag_service >> Edge(color=COLORS["data"], label="Sessions") >> chat_crud
    rag_service >> Edge(color=COLORS["data"], label="Messages") >> message_crud
    rag_service >> Edge(color=COLORS["data"], label="Cache") >> cache_manager

    # Collection Service Flow (Basic)
    collection_router >> Edge(color=COLORS["business"], label="CRUD") >> collection_service
    document_router >> Edge(color=COLORS["business"], label="Manage") >> document_service
    collection_service >> Edge(color=COLORS["data"], label="Store") >> collection_crud

    # Database Connections (All Working)
    (
        [user_crud, file_crud, chat_crud, collection_crud]
        >> Edge(color=COLORS["data"], label="SQL")
        >> postgres
    )
    [session_manager, cache_manager] >> Edge(color=COLORS["data"], label="Cache") >> redis
    [vector_manager, retrieval_service] >> Edge(color=COLORS["data"], label="Vectors") >> qdrant

    # External AI Connections (Working)
    embedding_service >> Edge(color=COLORS["ai"], label="Embeddings") >> openai_embed
    llm_service >> Edge(color=COLORS["ai"], label="Chat") >> openai_llm
    llm_service >> Edge(color=COLORS["ai"], style="dashed", label="Fallback") >> gemini_llm

    # Vector Search Integration
    vector_router >> Edge(color=COLORS["business"], label="Search") >> retrieval_service
    search_router >> Edge(color=COLORS["business"], label="Similarity") >> retrieval_service

    # Monitoring Connections
    llm_service >> Edge(color=COLORS["middleware"], style="dashed", label="Trace") >> langfuse
    (
        [auth_service, file_processor, rag_service]
        >> Edge(color=COLORS["middleware"], style="dashed", label="Metrics")
        >> prometheus
    )
    (
        [auth_router, upload_router, chat_router]
        >> Edge(color=COLORS["middleware"], style="dashed", label="Health")
        >> health_monitor
    )

    # Health Check Flow
    (
        shared_health
        >> Edge(color=COLORS["middleware"], style="dashed", label="Monitor")
        >> [postgres, redis, qdrant]
    )

print("✅ Generated: Backend Components Diagram (Updated - Operational RAG System)")
