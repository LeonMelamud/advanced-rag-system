#!/usr/bin/env python3
"""
Advanced RAG System - AI Processing Flow (Updated)
Visualizes the actual working AI/ML pipeline from document upload to response generation
Reflects the fully operational system with OpenAI integration and working RAG pipeline
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.ml import SagemakerModel
from diagrams.gcp.ml import AutoML
from diagrams.generic.compute import Rack
from diagrams.generic.storage import Storage
from diagrams.onprem.client import User
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Memcached
from diagrams.onprem.monitoring import Grafana
from diagrams.programming.framework import FastAPI

# Flow colors
COLORS = {
    "upload": "#3498db",  # Blue
    "processing": "#2ecc71",  # Green
    "embedding": "#9b59b6",  # Purple
    "retrieval": "#e74c3c",  # Red
    "generation": "#f39c12",  # Orange
    "evaluation": "#1abc9c",  # Teal
}

with Diagram(
    "Advanced RAG System - AI Processing Flow (Operational)",
    filename=str(Path(__file__).parent.parent / "generated" / "ai_processing_flow"),
    show=False,
    direction="TB",
    graph_attr={"fontsize": "18", "bgcolor": "white"},
):

    # Input
    user = User("User")

    # Document Processing Pipeline (✅ WORKING)
    with Cluster("Document Processing Pipeline (✅ OPERATIONAL)"):
        # Step 1: Upload (Working)
        upload_api = FastAPI("File Upload API\n(/api/v1/files/upload)")
        file_storage = Storage("File Storage\n(Local + Metadata)")

        # Step 2: Text Extraction (Working)
        text_extractor = Rack("Text Extractor\n(PyMuPDF + pandas)")

        # Step 3: Chunking (4 Strategies Implemented)
        with Cluster("Chunking Strategies (✅ IMPLEMENTED)"):
            fixed_chunker = Rack("Fixed Chunker\n(1000 chars)")
            recursive_chunker = Rack("Recursive Chunker\n(Semantic splits)")
            semantic_chunker = Rack("Semantic Chunker\n(NLP-based)")
            paragraph_chunker = Rack("Paragraph Chunker\n(Natural breaks)")

        # Step 4: Embedding Generation (Working with OpenAI)
        with Cluster("Embedding Generation (✅ WORKING)"):
            openai_embedder = SagemakerModel("OpenAI Embeddings\n(text-embedding-3-small)")
            gemini_embedder = AutoML("Google Embeddings\n(Alternative)")

        # Step 5: Vector Storage (Working)
        vector_db = Memcached("Qdrant Vector DB\n(2 Collections)")
        metadata_db = PostgreSQL("PostgreSQL\n(File Metadata)")

    # Query Processing Pipeline (✅ WORKING)
    with Cluster("Query Processing Pipeline (✅ OPERATIONAL)"):
        # Step 6: Query Input (Working)
        chat_api = FastAPI("Chat API\n(/api/v1/chat/message)")

        # Step 7: Authentication & Session (Working)
        auth_check = Rack("JWT Auth\n(Working)")
        session_manager = Rack("Session Manager\n(Redis)")

        # Step 8: RAG Pipeline (Working)
        with Cluster("RAG Service (✅ WORKING)"):
            query_processor = Rack("Query Processor\n(Preprocessing)")
            vector_search = Rack("Vector Search\n(Similarity)")
            context_merger = Rack("Context Merger\n(Enhanced RRF)")

        # Step 9: Context Assembly (Working)
        context_assembler = Rack("Context Assembler\n(Top-K Selection)")

    # LLM Generation Pipeline (✅ WORKING)
    with Cluster("LLM Generation Pipeline (✅ OPERATIONAL)"):
        # Step 10: LLM Request (Working)
        llm_request = Rack("LLM Request\n(Prompt + Context)")

        # Step 11: LLM Generation (Working with OpenAI)
        with Cluster("LLM Providers (✅ WORKING)"):
            openai_gpt4 = SagemakerModel("OpenAI GPT-4\n(Primary)")
            gemini_flash = AutoML("Gemini 2.0 Flash\n(Alternative)")

        # Step 12: Response Processing (Working)
        response_processor = Rack("Response Processor\n(Format + Sources)")

    # Data Persistence (✅ WORKING)
    with Cluster("Data Persistence (✅ OPERATIONAL)"):
        # Step 13: Chat Storage (Working)
        chat_storage = PostgreSQL("Chat Storage\n(Sessions + Messages)")

        # Step 14: Cache Management (Working)
        redis_cache = Memcached("Redis Cache\n(Session Data)")

    # Monitoring & Observability (Ready)
    with Cluster("Monitoring & Observability"):
        # Step 15: LLM Observability (Ready)
        langfuse = Grafana("Langfuse\n(LLM Tracing)")

        # Step 16: System Monitoring (Ready)
        health_monitor = Rack("Health Monitor\n(All Services)")

    # Document Processing Flow (✅ WORKING)
    user >> Edge(label="1. Upload Document", color=COLORS["upload"], style="bold") >> upload_api
    upload_api >> Edge(color=COLORS["upload"], label="Store") >> file_storage
    (
        file_storage
        >> Edge(label="2. Extract Text", color=COLORS["processing"], style="bold")
        >> text_extractor
    )

    # Chunking Flow (✅ WORKING)
    text_extractor >> Edge(label="3a. Fixed Chunks", color=COLORS["processing"]) >> fixed_chunker
    text_extractor >> Edge(label="3b. Recursive", color=COLORS["processing"]) >> recursive_chunker
    text_extractor >> Edge(label="3c. Semantic", color=COLORS["processing"]) >> semantic_chunker
    text_extractor >> Edge(label="3d. Paragraph", color=COLORS["processing"]) >> paragraph_chunker

    # Embedding Flow (✅ WORKING)
    (
        [fixed_chunker, recursive_chunker, semantic_chunker, paragraph_chunker]
        >> Edge(label="4. Generate Embeddings", color=COLORS["embedding"], style="bold")
        >> openai_embedder
    )
    (
        [fixed_chunker, recursive_chunker, semantic_chunker, paragraph_chunker]
        >> Edge(color=COLORS["embedding"], style="dashed")
        >> gemini_embedder
    )

    # Storage Flow (✅ WORKING)
    (
        openai_embedder
        >> Edge(label="5a. Store Vectors", color=COLORS["embedding"], style="bold")
        >> vector_db
    )
    openai_embedder >> Edge(label="5b. Store Metadata", color=COLORS["embedding"]) >> metadata_db

    # Query Processing Flow (✅ WORKING)
    user >> Edge(label="6. Submit Query", color=COLORS["retrieval"], style="bold") >> chat_api
    chat_api >> Edge(label="7a. Authenticate", color=COLORS["retrieval"]) >> auth_check
    auth_check >> Edge(label="7b. Session", color=COLORS["retrieval"]) >> session_manager
    (
        session_manager
        >> Edge(label="8. Process Query", color=COLORS["retrieval"], style="bold")
        >> query_processor
    )

    # RAG Pipeline Flow (✅ WORKING)
    (
        query_processor
        >> Edge(label="9a. Vector Search", color=COLORS["retrieval"], style="bold")
        >> vector_search
    )
    (
        vector_search
        >> Edge(label="9b. Merge Context", color=COLORS["retrieval"], style="bold")
        >> context_merger
    )
    (
        context_merger
        >> Edge(label="10. Assemble Context", color=COLORS["retrieval"], style="bold")
        >> context_assembler
    )

    # LLM Generation Flow (✅ WORKING)
    (
        context_assembler
        >> Edge(label="11. Create Request", color=COLORS["generation"], style="bold")
        >> llm_request
    )
    (
        llm_request
        >> Edge(label="12a. Primary LLM", color=COLORS["generation"], style="bold")
        >> openai_gpt4
    )
    (
        llm_request
        >> Edge(label="12b. Alternative", color=COLORS["generation"], style="dashed")
        >> gemini_flash
    )

    # Response Processing (✅ WORKING)
    (
        [openai_gpt4, gemini_flash]
        >> Edge(label="13. Process Response", color=COLORS["generation"], style="bold")
        >> response_processor
    )

    # Data Persistence Flow (✅ WORKING)
    response_processor >> Edge(label="14a. Store Chat", color=COLORS["evaluation"]) >> chat_storage
    response_processor >> Edge(label="14b. Cache Data", color=COLORS["evaluation"]) >> redis_cache

    # Monitoring Flow (Ready)
    (
        openai_gpt4
        >> Edge(label="15a. Trace LLM", color=COLORS["evaluation"], style="dashed")
        >> langfuse
    )
    (
        [upload_api, chat_api]
        >> Edge(label="15b. Health Check", color=COLORS["evaluation"], style="dashed")
        >> health_monitor
    )

    # Final Response (✅ WORKING)
    (
        response_processor
        >> Edge(label="16. Return Response", color=COLORS["generation"], style="bold")
        >> user
    )

    # Database Connections (✅ WORKING)
    vector_search >> Edge(color=COLORS["retrieval"], style="dashed") >> vector_db
    session_manager >> Edge(color=COLORS["retrieval"], style="dashed") >> redis_cache

    # Status Indicators
    with Cluster("System Status"):
        status_working = Rack("✅ OPERATIONAL\n(Auth, File, Chat, RAG)")
        status_ready = Rack("🔧 READY\n(Monitoring, Analytics)")
        status_future = Rack("📋 PLANNED\n(Advanced Features)")

print("✅ Generated: AI Processing Flow Diagram (Updated - Operational System)")
