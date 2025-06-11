# Architecture Diagrams Documentation

## Overview

This document outlines the architecture visualization strategy for the Advanced RAG System using the [diagrams](https://diagrams.mingrammer.com/docs/getting-started/installation) Python library. The diagrams provide visual representations of our system architecture, data flows, and component relationships.

## Diagrams Library Setup

### Installation Requirements

Based on the [official documentation](https://diagrams.mingrammer.com/docs/getting-started/installation), the diagrams library requires:

- **Python 3.7+** (we're using Python 3.11+)
- **Graphviz** for rendering diagrams

### Installation Steps

```bash
# Install Graphviz (macOS with Homebrew)
brew install graphviz

# Install diagrams library
pip install diagrams

# Verify installation
python -c "import diagrams; print('Diagrams installed successfully')"
```

### Project Structure

```
diagrams/
├── architecture/          # High-level system architecture diagrams
├── flows/                # Process and data flow diagrams  
├── components/           # Component relationship diagrams
├── generated/            # Auto-generated diagram files (.png, .svg)
└── scripts/              # Python scripts for diagram generation
```

## Best Practices for Diagrams

### 1. Naming Conventions
```python
# Use descriptive, consistent naming
with Diagram("Advanced RAG System - Microservices Architecture", 
             filename="architecture/microservices_overview",
             show=False, 
             direction="TB"):  # Top to Bottom
```

### 2. Color Coding Strategy
```python
# Consistent color scheme across all diagrams
COLORS = {
    "frontend": "#3498db",      # Blue
    "backend": "#2ecc71",       # Green  
    "database": "#e74c3c",      # Red
    "ai_services": "#9b59b6",   # Purple
    "infrastructure": "#f39c12", # Orange
    "external": "#95a5a6"       # Gray
}
```

### 3. Grouping and Clustering
```python
# Use clusters for logical grouping
with Cluster("Backend Services"):
    auth_service = FastAPI("Auth Service")
    file_service = FastAPI("File Service")
    chat_service = FastAPI("Chat Service")
```

### 4. Consistent Icon Usage
```python
# Use appropriate icons for each component type
from diagrams.aws.compute import Lambda, ECS
from diagrams.aws.database import RDS, Dynamodb
from diagrams.aws.network import ELB, CloudFront
from diagrams.onprem.client import Users
from diagrams.programming.framework import React, FastAPI
```

## Diagram Specifications

### 1. System Architecture Diagrams

#### 1.1 High-Level System Overview
**File**: `diagrams/architecture/system_overview.py`
**Purpose**: Complete system architecture showing all major components
**Components**:
- Frontend (React)
- API Gateway
- Microservices (6 services)
- Databases (PostgreSQL, Redis, Qdrant)
- External APIs (Gemini, OpenAI)
- Infrastructure components

#### 1.2 Microservices Architecture
**File**: `diagrams/architecture/microservices_detail.py`
**Purpose**: Detailed view of microservices interactions
**Components**:
- Service-to-service communication
- Database per service pattern
- Shared components
- Message queues

#### 1.3 Infrastructure Architecture
**File**: `diagrams/architecture/infrastructure.py`
**Purpose**: Deployment and infrastructure view
**Components**:
- Docker containers
- Kubernetes clusters
- Load balancers
- Monitoring stack
- CI/CD pipeline

### 2. Component Diagrams

#### 2.1 Backend Components
**File**: `diagrams/components/backend_components.py`
**Purpose**: Internal structure of backend services
**Components**:
- FastAPI routers
- Business logic layers
- Data access layers
- Shared utilities

#### 2.2 Frontend Components
**File**: `diagrams/components/frontend_components.py`
**Purpose**: React application structure
**Components**:
- React components hierarchy
- State management
- API integration
- UI component library

#### 2.3 Database Schema Relationships
**File**: `diagrams/components/database_schema.py`
**Purpose**: Database relationships and data flow
**Components**:
- PostgreSQL tables
- Vector database collections
- Cache layers
- Data relationships

### 3. Flow Diagrams

#### 3.1 AI Processing Flow
**File**: `diagrams/flows/ai_processing_flow.py`
**Purpose**: Complete AI/ML pipeline visualization
**Flow Steps**:
1. Document upload
2. Text extraction
3. Chunking strategies
4. Embedding generation
5. Vector storage
6. Query processing
7. Retrieval pipeline
8. LLM generation
9. Response assembly

#### 3.2 User Request Flow
**File**: `diagrams/flows/user_request_flow.py`
**Purpose**: End-to-end user interaction flow
**Flow Steps**:
1. User query input
2. Authentication
3. Query processing
4. Vector search
5. Context assembly
6. LLM generation
7. Response delivery
8. Feedback collection

#### 3.3 Data Processing Pipeline
**File**: `diagrams/flows/data_pipeline.py`
**Purpose**: Document processing and indexing flow
**Flow Steps**:
1. File upload
2. Format detection
3. Text extraction
4. Preprocessing
5. Chunking
6. Embedding
7. Vector indexing
8. Metadata storage

#### 3.4 Multi-Provider LLM Flow
**File**: `diagrams/flows/llm_fallback_flow.py`
**Purpose**: LLM provider selection and fallback logic
**Flow Steps**:
1. Query complexity assessment
2. Primary provider selection (Gemini)
3. Fallback logic (OpenAI)
4. Response generation
5. Quality evaluation
6. Provider performance tracking

## Diagram Generation Scripts

### Master Generation Script
**File**: `diagrams/generate_all.py`
```python
#!/usr/bin/env python3
"""
Master script to generate all architecture diagrams
Usage: python diagrams/generate_all.py
"""

import subprocess
import sys
from pathlib import Path

def generate_diagram(script_path):
    """Generate a single diagram"""
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Generated: {script_path}")
        else:
            print(f"❌ Failed: {script_path}")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error generating {script_path}: {e}")

def main():
    """Generate all diagrams"""
    diagrams_dir = Path(__file__).parent
    
    # Architecture diagrams
    generate_diagram(diagrams_dir / "architecture" / "system_overview.py")
    generate_diagram(diagrams_dir / "architecture" / "microservices_detail.py")
    generate_diagram(diagrams_dir / "architecture" / "infrastructure.py")
    
    # Component diagrams
    generate_diagram(diagrams_dir / "components" / "backend_components.py")
    generate_diagram(diagrams_dir / "components" / "frontend_components.py")
    generate_diagram(diagrams_dir / "components" / "database_schema.py")
    
    # Flow diagrams
    generate_diagram(diagrams_dir / "flows" / "ai_processing_flow.py")
    generate_diagram(diagrams_dir / "flows" / "user_request_flow.py")
    generate_diagram(diagrams_dir / "flows" / "data_pipeline.py")
    generate_diagram(diagrams_dir / "flows" / "llm_fallback_flow.py")

if __name__ == "__main__":
    main()
```

## Diagram Maintenance

### 1. Version Control
- Store diagram scripts in version control
- Generate diagrams as part of CI/CD pipeline
- Keep generated images in `diagrams/generated/` directory

### 2. Documentation Updates
- Update diagrams when architecture changes
- Include diagram generation in development workflow
- Review diagrams during architecture reviews

### 3. Export Formats
```python
# Support multiple output formats
with Diagram("System Overview", 
             filename="system_overview",
             show=False,
             outformat="png"):  # or "svg", "pdf"
```

### 4. Automation
```bash
# Add to package.json scripts or Makefile
generate-diagrams:
    python diagrams/generate_all.py
    
update-docs:
    python diagrams/generate_all.py
    git add diagrams/generated/
    git commit -m "Update architecture diagrams"
```

## Integration with Documentation

### 1. README Integration
```markdown
## Architecture Overview

![System Overview](diagrams/generated/system_overview.png)

For detailed architecture documentation, see [Architecture Diagrams](memory-bank/architecture-diagrams.md).
```

### 2. Memory Bank Integration
- Link diagrams in relevant Memory Bank documents
- Include diagram references in implementation guides
- Use diagrams for onboarding new team members

### 3. Presentation Ready
- Generate high-resolution diagrams for presentations
- Create simplified versions for executive summaries
- Maintain consistent branding across all diagrams

## Next Steps

1. **Install Dependencies**: Set up diagrams library and Graphviz
2. **Create Base Scripts**: Implement the core diagram generation scripts
3. **Generate Initial Set**: Create first version of all specified diagrams
4. **Integrate with Docs**: Link diagrams into existing documentation
5. **Automate Generation**: Set up automated diagram updates

---
*Last Updated: Current Session*
*Next Update: After diagram scripts are implemented* 