#!/usr/bin/env python3
"""
Advanced RAG System - Infrastructure Architecture
Shows deployment, containers, and infrastructure components
"""

from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.storage import S3
from diagrams.generic.compute import Rack
from diagrams.k8s.compute import Deployment, Pod
from diagrams.k8s.network import Ingress, Service
from diagrams.k8s.storage import PV, PVC
from diagrams.onprem.client import Users
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Memcached, Redis
from diagrams.onprem.logging import FluentBit
from diagrams.onprem.monitoring import Grafana, Prometheus
from diagrams.onprem.network import Internet, Nginx
from diagrams.programming.framework import React

# Infrastructure colors
COLORS = {
    "external": "#95a5a6",  # Gray
    "ingress": "#3498db",  # Blue
    "services": "#2ecc71",  # Green
    "data": "#e74c3c",  # Red
    "monitoring": "#f39c12",  # Orange
    "storage": "#9b59b6",  # Purple
}

with Diagram(
    "Advanced RAG System - Infrastructure Architecture",
    filename=str(Path(__file__).parent.parent / "generated" / "infrastructure"),
    show=False,
    direction="TB",
    graph_attr={"fontsize": "18", "bgcolor": "white"},
):

    # External
    users = Users("Users")
    internet = Internet("Internet")

    # CDN & Load Balancer
    with Cluster("Edge Layer"):
        cdn = S3("CDN\n(CloudFront)")
        load_balancer = Nginx("Load Balancer\n(AWS ALB)")

    # Kubernetes Cluster
    with Cluster("Kubernetes Cluster"):
        # Ingress Layer
        with Cluster("Ingress Layer"):
            ingress = Ingress("Ingress Controller\n(Nginx)")
            tls_termination = Rack("TLS Termination\n(Let's Encrypt)")

        # Frontend Services
        with Cluster("Frontend Services"):
            frontend_service = Service("Frontend Service")
            frontend_pods = [Pod("React Pod 1"), Pod("React Pod 2")]

        # Backend Services
        with Cluster("Backend Services"):
            # Auth Service
            with Cluster("Auth Service"):
                auth_service = Service("Auth Service")
                auth_deployment = Deployment("Auth Deployment")
                auth_pods = [Pod("Auth Pod 1"), Pod("Auth Pod 2")]

            # File Service
            with Cluster("File Service"):
                file_service = Service("File Service")
                file_deployment = Deployment("File Deployment")
                file_pods = [Pod("File Pod 1"), Pod("File Pod 2")]

            # Chat Service
            with Cluster("Chat Service"):
                chat_service = Service("Chat Service")
                chat_deployment = Deployment("Chat Deployment")
                chat_pods = [Pod("Chat Pod 1"), Pod("Chat Pod 2"), Pod("Chat Pod 3")]

            # Collection Service
            with Cluster("Collection Service"):
                collection_service = Service("Collection Service")
                collection_deployment = Deployment("Collection Deployment")
                collection_pods = [Pod("Collection Pod 1"), Pod("Collection Pod 2")]

        # Data Layer
        with Cluster("Data Layer"):
            # PostgreSQL
            with Cluster("PostgreSQL Cluster"):
                postgres_service = Service("PostgreSQL Service")
                postgres_primary = Pod("PostgreSQL Primary")
                postgres_replica = Pod("PostgreSQL Replica")
                postgres_pvc = PVC("PostgreSQL PVC")
                postgres_pv = PV("PostgreSQL PV")

            # Redis
            with Cluster("Redis Cluster"):
                redis_service = Service("Redis Service")
                redis_master = Pod("Redis Master")
                redis_replica = Pod("Redis Replica")
                redis_pvc = PVC("Redis PVC")

            # Qdrant Vector DB
            with Cluster("Qdrant Cluster"):
                qdrant_service = Service("Qdrant Service")
                qdrant_pods = [Pod("Qdrant Pod 1"), Pod("Qdrant Pod 2")]
                qdrant_pvc = PVC("Qdrant PVC")
                qdrant_pv = PV("Qdrant PV")

        # Monitoring Stack
        with Cluster("Monitoring Stack"):
            # Prometheus
            prometheus_service = Service("Prometheus Service")
            prometheus_pod = Pod("Prometheus Pod")
            prometheus_pvc = PVC("Prometheus PVC")

            # Grafana
            grafana_service = Service("Grafana Service")
            grafana_pod = Pod("Grafana Pod")

            # Langfuse
            langfuse_service = Service("Langfuse Service")
            langfuse_pod = Pod("Langfuse Pod")

            # Logging
            logging_service = Service("Logging Service")
            elasticsearch_pod = Pod("Elasticsearch Pod")
            kibana_pod = Pod("Kibana Pod")
            fluentd_pod = Pod("FluentBit Pod")

    # External Storage
    with Cluster("External Storage"):
        file_storage = S3("File Storage\n(S3/MinIO)")
        backup_storage = S3("Backup Storage\n(S3 Glacier)")

    # External AI Services
    with Cluster("External AI Services"):
        gemini_api = Rack("Google Gemini API\n(Primary LLM)")
        openai_api = Rack("OpenAI API\n(Fallback LLM)")

    # User Flow
    users >> Edge(color=COLORS["external"]) >> internet
    internet >> Edge(color=COLORS["external"]) >> cdn
    cdn >> Edge(color=COLORS["ingress"]) >> load_balancer
    load_balancer >> Edge(color=COLORS["ingress"]) >> ingress

    # Ingress Flow
    ingress >> Edge(color=COLORS["ingress"]) >> tls_termination
    (
        tls_termination
        >> Edge(color=COLORS["ingress"])
        >> [frontend_service, auth_service, file_service, chat_service, collection_service]
    )

    # Frontend Flow
    frontend_service >> Edge(color=COLORS["services"]) >> frontend_pods

    # Backend Service Flows
    auth_service >> Edge(color=COLORS["services"]) >> auth_deployment >> auth_pods
    file_service >> Edge(color=COLORS["services"]) >> file_deployment >> file_pods
    chat_service >> Edge(color=COLORS["services"]) >> chat_deployment >> chat_pods
    collection_service >> Edge(color=COLORS["services"]) >> collection_deployment >> collection_pods

    # Data Connections
    for pod_group in [auth_pods, file_pods, chat_pods, collection_pods]:
        for pod in pod_group:
            pod >> Edge(color=COLORS["data"]) >> postgres_service
    postgres_service >> Edge(color=COLORS["data"]) >> postgres_primary
    postgres_primary >> Edge(color=COLORS["data"], style="dashed") >> postgres_replica
    postgres_primary >> Edge(color=COLORS["storage"]) >> postgres_pvc >> postgres_pv

    for pod_group in [auth_pods, chat_pods]:
        for pod in pod_group:
            pod >> Edge(color=COLORS["data"]) >> redis_service
    redis_service >> Edge(color=COLORS["data"]) >> redis_master
    redis_master >> Edge(color=COLORS["data"], style="dashed") >> redis_replica
    redis_master >> Edge(color=COLORS["storage"]) >> redis_pvc

    for pod_group in [file_pods, chat_pods]:
        for pod in pod_group:
            pod >> Edge(color=COLORS["data"]) >> qdrant_service
    qdrant_service >> Edge(color=COLORS["data"]) >> qdrant_pods
    for pod in qdrant_pods:
        pod >> Edge(color=COLORS["storage"]) >> qdrant_pvc
    qdrant_pvc >> Edge(color=COLORS["storage"]) >> qdrant_pv

    # External Storage Connections
    for pod in file_pods:
        pod >> Edge(color=COLORS["storage"]) >> file_storage
    postgres_primary >> Edge(color=COLORS["storage"], style="dashed") >> backup_storage
    for pod in qdrant_pods:
        pod >> Edge(color=COLORS["storage"], style="dashed") >> backup_storage

    # AI Service Connections
    for pod_group in [file_pods, chat_pods]:
        for pod in pod_group:
            pod >> Edge(color=COLORS["external"]) >> gemini_api
            pod >> Edge(color=COLORS["external"], style="dashed") >> openai_api

    # Monitoring Connections
    prometheus_service >> Edge(color=COLORS["monitoring"]) >> prometheus_pod
    prometheus_pod >> Edge(color=COLORS["monitoring"]) >> prometheus_pvc

    grafana_service >> Edge(color=COLORS["monitoring"]) >> grafana_pod
    prometheus_pod >> Edge(color=COLORS["monitoring"]) >> grafana_pod

    langfuse_service >> Edge(color=COLORS["monitoring"]) >> langfuse_pod

    (
        logging_service
        >> Edge(color=COLORS["monitoring"])
        >> [elasticsearch_pod, kibana_pod, fluentd_pod]
    )

    # Monitoring Data Collection
    for pod_group in [auth_pods, file_pods, chat_pods, collection_pods]:
        for pod in pod_group:
            pod >> Edge(color=COLORS["monitoring"], style="dashed") >> prometheus_pod
            pod >> Edge(color=COLORS["monitoring"], style="dashed") >> langfuse_pod
            pod >> Edge(color=COLORS["monitoring"], style="dashed") >> fluentd_pod

print("✅ Generated: Infrastructure Architecture Diagram")
