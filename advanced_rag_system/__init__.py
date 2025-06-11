"""
Advanced RAG System with File Analysis and AI Chat.

A sophisticated Retrieval Augmented Generation (RAG) system designed to ingest,
process, and understand diverse file types, making their content accessible
through an intelligent AI chat interface.
"""

__version__ = "0.1.0"
__author__ = "Leon Melamud"
__email__ = "leon.melamud@example.com"

# Import main components for easy access
from backend.common.schemas import (
    ChatRequest,
    ChatResponse,
    ChunkingStrategy,
    Collection,
    EmbeddingModel,
    FileType,
    LLMModel,
    ProcessingStatus,
)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "FileType",
    "ProcessingStatus",
    "ChunkingStrategy",
    "EmbeddingModel",
    "LLMModel",
    "Collection",
    "ChatRequest",
    "ChatResponse",
]
