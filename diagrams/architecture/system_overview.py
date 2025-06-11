#!/usr/bin/env python3
"""
Advanced RAG System - High-Level System Overview
Generates a comprehensive architecture diagram showing all major components
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.ml import SagemakerModel
from diagrams.gcp.ml import AutoML
from diagrams.generic.compute import Rack
from diagrams.generic.storage import Storage
from diagrams.onprem.client import Users
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Memcached, Redis
from diagrams.onprem.logging import FluentBit
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Nginx
from diagrams.programming.framework import FastAPI, React

# Color scheme for consistent styling
COLORS = {
    "user_flow": "#3498db",  # Blue
    "api_flow": "#2ecc71",  # Green
    "data_flow": "#e74c3c",  # Red
    "ai_flow": "#9b59b6",  # Purple
    "monitoring": "#f39c12",  # Orange
}

with Diagram(
    "Advanced RAG System - High-Level Architecture",
    filename=str(Path(__file__).parent.parent / "generated" / "system_overview"),
    show=False,
    direction="TB",
    graph_attr={"fontsize": "20", "bgcolor": "white"},
):

    # Users
    users = Users("Users")

    # Frontend Layer
    with Cluster("Frontend Layer"):
        frontend = React("React App\n(TypeScript)")
        cdn = Storage("CDN\n(Static Assets)")

    # API Gateway Layer
    with Cluster("API Gateway"):
        gateway = Nginx("API Gateway\n(Nginx/Kong)")
        load_balancer = Rack("Load Balancer")

    # Backend Microservices
    with Cluster("Backend Microservices"):
        with Cluster("Core Services"):
            auth_service = FastAPI("Auth Service\n(JWT, RBAC)")
            file_service = FastAPI("File Service\n(Upload, Processing)")
            chat_service = FastAPI("Chat Service\n(RAG Core)")
            collection_service = FastAPI("Collection Service\n(Management)")

        with Cluster("Optional Services"):
            mcp_service = FastAPI("MCP Orchestrator\n(Tools Integration)")
            api_config = FastAPI("API Gateway Config\n(Routing)")

    # AI/ML Services
    with Cluster("AI/ML Services"):
        gemini_primary = AutoML("Google Gemini\n(Primary LLM)")
        gemini_embedding = AutoML("Google Embedding\n(text-embedding-004)")
        openai_fallback = SagemakerModel("OpenAI GPT-4o\n(Fallback LLM)")
        openai_embedding = SagemakerModel("OpenAI Embedding\n(text-embedding-3-small)")

    # Data Layer
    with Cluster("Data Layer"):
        with Cluster("Databases"):
            postgres = PostgreSQL("PostgreSQL\n(Metadata, Users)")
            vector_db = Memcached("Qdrant\n(Vector Database)")
            cache = Redis("Redis\n(Cache, Sessions)")

        with Cluster("Storage"):
            file_storage = Storage("File Storage\n(Documents, Media)")
            backup_storage = Storage("Backup Storage\n(Disaster Recovery)")

    # Monitoring & Observability
    with Cluster("Monitoring & Observability"):
        langfuse = Grafana("Langfuse\n(LLM Observability)")
        prometheus = Prometheus("Prometheus\n(Metrics)")
        grafana = Grafana("Grafana\n(Dashboards)")
        logging = FluentBit("Centralized Logging\n(ELK Stack)")

    # User Flow
    users >> Edge(color=COLORS["user_flow"], style="bold") >> frontend
    frontend >> Edge(color=COLORS["user_flow"]) >> cdn
    frontend >> Edge(color=COLORS["api_flow"], style="bold") >> gateway

    # API Gateway Flow
    gateway >> Edge(color=COLORS["api_flow"]) >> load_balancer
    (
        load_balancer
        >> Edge(color=COLORS["api_flow"])
        >> [auth_service, file_service, chat_service, collection_service]
    )

    # Service Interactions
    auth_service >> Edge(color=COLORS["data_flow"]) >> postgres
    file_service >> Edge(color=COLORS["data_flow"]) >> [file_storage, postgres]
    chat_service >> Edge(color=COLORS["data_flow"]) >> [vector_db, cache]
    collection_service >> Edge(color=COLORS["data_flow"]) >> [postgres, vector_db]

    # AI Service Connections
    (
        file_service
        >> Edge(color=COLORS["ai_flow"], style="bold")
        >> [gemini_embedding, openai_embedding]
    )
    chat_service >> Edge(color=COLORS["ai_flow"], style="bold") >> [gemini_primary, openai_fallback]

    # Monitoring Connections
    (
        [auth_service, file_service, chat_service, collection_service]
        >> Edge(color=COLORS["monitoring"], style="dashed")
        >> langfuse
    )
    (
        [auth_service, file_service, chat_service, collection_service]
        >> Edge(color=COLORS["monitoring"], style="dashed")
        >> prometheus
    )
    prometheus >> Edge(color=COLORS["monitoring"]) >> grafana
    (
        [auth_service, file_service, chat_service, collection_service]
        >> Edge(color=COLORS["monitoring"], style="dashed")
        >> logging
    )

    # Data Backup
    [postgres, vector_db] >> Edge(color=COLORS["data_flow"], style="dashed") >> backup_storage

print("✅ Generated: System Overview Diagram")
