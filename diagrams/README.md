# Architecture Diagrams - Advanced RAG System

This directory contains Python scripts to generate visual architecture diagrams for the **fully operational** Advanced RAG System using the [diagrams](https://diagrams.mingrammer.com/) library.

## 🎉 **Current Status: FULLY OPERATIONAL RAG SYSTEM**

The diagrams now reflect the **actual working implementation** with:
- ✅ **Complete authentication system** (JWT + user management)
- ✅ **Operational file processing** (multi-format support)
- ✅ **Working vector database** (Qdrant integration)
- ✅ **Functional RAG pipeline** (OpenAI GPT-4 integration)
- ✅ **Database integration** (PostgreSQL + Redis + Qdrant)

## Quick Start

### 1. Install Dependencies

```bash
# Install Graphviz (required for diagram rendering)
brew install graphviz  # macOS
# sudo apt-get install graphviz  # Ubuntu/Debian
# choco install graphviz  # Windows

# Install Python diagrams library
pip install diagrams
```

### 2. Generate All Diagrams

```bash
# From the project root
python diagrams/generate_all.py
```

### 3. View Generated Diagrams

Generated PNG files will be in `diagrams/generated/`:
- `system_overview.png` - High-level system architecture
- `infrastructure.png` - Deployment and infrastructure view
- `backend_components.png` - **Updated**: Operational backend microservices
- `frontend_components.png` - React application structure
- `ai_processing_flow.png` - **Updated**: Working AI/ML pipeline flow

## Directory Structure

```
diagrams/
├── README.md                    # This file (Updated)
├── generate_all.py             # Master generation script
├── architecture/               # High-level system diagrams
│   ├── system_overview.py      # Complete system architecture
│   └── infrastructure.py       # Deployment infrastructure
├── components/                 # Component relationship diagrams
│   ├── backend_components.py   # **Updated**: Operational backend services
│   └── frontend_components.py  # React application
├── flows/                      # Process and data flow diagrams
│   └── ai_processing_flow.py   # **Updated**: Working AI/ML pipeline
└── generated/                  # Auto-generated diagram files
    ├── system_overview.png     # (296.1 KB)
    ├── infrastructure.png      # (531.7 KB)
    ├── backend_components.png  # **Updated** (730.3 KB)
    ├── frontend_components.png # (606.5 KB)
    └── ai_processing_flow.png  # **Updated** (645.7 KB)
```

## Individual Diagram Generation

You can generate individual diagrams by running the specific Python scripts:

```bash
# Generate system overview
python diagrams/architecture/system_overview.py

# Generate updated AI processing flow
python diagrams/flows/ai_processing_flow.py

# Generate updated backend components
python diagrams/components/backend_components.py
```

## Diagram Types

### 1. Architecture Diagrams (`architecture/`)

**System Overview** (`system_overview.py`)
- Complete system architecture showing all major components
- Frontend, backend services, databases, AI services
- External integrations and monitoring stack
- Color-coded by component type

**Infrastructure** (`infrastructure.py`)
- Kubernetes deployment view
- Container orchestration and scaling
- Load balancers, ingress, and networking
- Storage and backup strategies

### 2. Component Diagrams (`components/`)

**Backend Components** (`backend_components.py`) - **✅ UPDATED**
- **Reflects actual operational system** with working authentication
- **Real RAG pipeline implementation** with OpenAI integration
- **DRY architecture patterns** with shared components
- **Working database connections** (PostgreSQL, Redis, Qdrant)
- **Operational API endpoints** with proper routing
- **External AI service integration** (OpenAI GPT-4, embeddings)

**Frontend Components** (`frontend_components.py`)
- React application structure and hierarchy
- Component relationships and data flow
- State management and API integration
- UI component library organization

### 3. Flow Diagrams (`flows/`)

**AI Processing Flow** (`ai_processing_flow.py`) - **✅ UPDATED**
- **Complete operational AI/ML pipeline** from upload to response
- **Working document processing** with 4 chunking strategies
- **Functional embedding generation** with OpenAI API
- **Operational vector storage** and similarity search
- **Working RAG pipeline** with context merging
- **Functional LLM integration** with GPT-4
- **Real authentication and session management**

## 🎯 **What's New in Updated Diagrams**

### **Backend Components (Updated)**
- **✅ Operational Status**: Shows actual working services vs. planned
- **✅ Real Authentication**: JWT middleware and user management
- **✅ Working File Processing**: Multi-format support with PyMuPDF
- **✅ Functional Vector Database**: Qdrant integration with 2 collections
- **✅ Complete RAG Pipeline**: Query processing → Vector search → LLM generation
- **✅ External AI Integration**: OpenAI GPT-4 and embeddings working
- **✅ DRY Architecture**: Shared components and service factory pattern

### **AI Processing Flow (Updated)**
- **✅ Working Pipeline**: End-to-end operational flow
- **✅ Real API Endpoints**: Actual `/api/v1/` routes
- **✅ Authentication Flow**: JWT validation and session management
- **✅ 4 Chunking Strategies**: Fixed, recursive, semantic, paragraph
- **✅ OpenAI Integration**: Primary embedding and LLM provider
- **✅ Database Persistence**: Chat sessions and message storage
- **✅ Status Indicators**: Clear operational vs. planned features

## Customization

### Color Scheme

Each diagram uses a consistent color scheme:
- **Blue (#3498db)**: User interactions, frontend, API flows
- **Green (#2ecc71)**: Backend services, business logic, working components
- **Red (#e74c3c)**: Data flow, databases, storage
- **Purple (#9b59b6)**: AI services, embeddings, shared components
- **Orange (#f39c12)**: Infrastructure, monitoring, LLM generation
- **Teal (#1abc9c)**: Utilities, evaluation, AI processing
- **Gray (#95a5a6)**: External services, future enhancements

### Status Indicators

The updated diagrams include clear status indicators:
- **✅ OPERATIONAL**: Fully working components
- **🔧 READY**: Implemented but not critical path
- **📋 PLANNED**: Future enhancements

### Adding New Diagrams

1. Create a new Python script in the appropriate directory
2. Follow the existing pattern and color scheme
3. Add the script to `generate_all.py`
4. Test generation with the individual script first

### Example Template

```python
#!/usr/bin/env python3
"""
Description of your diagram
"""

from pathlib import Path
from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import FastAPI
# ... other imports

with Diagram("Your Diagram Title", 
             filename=str(Path(__file__).parent.parent / "generated" / "your_diagram"),
             show=False, 
             direction="TB"):
    
    # Your diagram components here
    pass

print("✅ Generated: Your Diagram")
```

## Troubleshooting

### Common Issues

**"Graphviz not found"**
```bash
# Install Graphviz first
brew install graphviz  # macOS
```

**"diagrams module not found"**
```bash
# Install the diagrams library
pip install diagrams
```

**"Permission denied"**
```bash
# Make scripts executable
chmod +x diagrams/generate_all.py
```

**Diagram generation timeout**
- Large diagrams may take time to render
- The timeout is set to 60 seconds per diagram
- Check for circular dependencies in your diagram

### Debugging

Run individual scripts to isolate issues:
```bash
python diagrams/components/backend_components.py
```

Check the error output for specific issues with imports or diagram syntax.

## Integration with Documentation

The generated diagrams are referenced in:
- `memory-bank/project_structure.md` - Project structure documentation
- `README.md` - Project overview
- Implementation guides and technical documentation

## Recent Updates (January 2, 2025)

### **✅ Major Diagram Updates**
- **Backend Components**: Updated to reflect fully operational RAG system
- **AI Processing Flow**: Updated to show working OpenAI integration
- **Status Accuracy**: All diagrams now reflect actual implementation state
- **Performance**: All 5 diagrams generate successfully in 2.4 seconds

### **✅ System Achievements Reflected**
- **Complete Authentication**: JWT system with user management
- **Operational File Processing**: Multi-format document support
- **Working Vector Database**: Qdrant with 2 collections operational
- **Functional RAG Pipeline**: End-to-end query → response working
- **External AI Integration**: OpenAI GPT-4 and embeddings operational

## Automation

### CI/CD Integration

Add to your CI/CD pipeline:
```yaml
- name: Generate Architecture Diagrams
  run: |
    pip install diagrams
    python diagrams/generate_all.py
    
- name: Commit Updated Diagrams
  run: |
    git add diagrams/generated/
    git commit -m "Update architecture diagrams" || exit 0
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: generate-diagrams
      name: Generate Architecture Diagrams
      entry: python diagrams/generate_all.py
      language: system
      files: ^diagrams/.*\.py$
```

## Best Practices

1. **Keep diagrams current** - Update when implementation changes
2. **Use consistent naming** - Follow established conventions
3. **Update regularly** - Regenerate when architecture evolves
4. **Version control scripts** - Track diagram logic changes
5. **Document changes** - Update this README when adding diagrams
6. **Reflect reality** - Ensure diagrams match actual implementation

---

**Status**: ✅ All diagrams reflect the fully operational Advanced RAG System  
**Last Updated**: January 2, 2025 - Evening  
**Next Update**: When new features are implemented or architecture changes 