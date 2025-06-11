"""
Embedding Service
Generates text embeddings using various providers following DRY principles
"""

import asyncio
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import openai
from openai import AsyncOpenAI


class BaseEmbedder(ABC):
    """Base class for embedding providers following DRY principles"""

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension"""
        pass

    def _validate_text(self, text: str) -> str:
        """Validate and clean text for embedding"""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        # Remove excessive whitespace
        text = " ".join(text.split())

        # Truncate if too long (most models have token limits)
        max_chars = 8000  # Conservative limit
        if len(text) > max_chars:
            text = text[:max_chars]

        return text


class OpenAIEmbedder(BaseEmbedder):
    """OpenAI embedding provider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)

        # Model configurations
        self.model_configs = {
            "text-embedding-3-small": {"dimension": 1536, "max_tokens": 8191},
            "text-embedding-3-large": {"dimension": 3072, "max_tokens": 8191},
            "text-embedding-ada-002": {"dimension": 1536, "max_tokens": 8191},
        }

        if model not in self.model_configs:
            raise ValueError(f"Unsupported model: {model}")

    def get_model_name(self) -> str:
        return self.model

    def get_embedding_dimension(self) -> int:
        return self.model_configs[self.model]["dimension"]

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        text = self._validate_text(text)

        try:
            response = await self.client.embeddings.create(model=self.model, input=text)
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"OpenAI embedding generation failed: {str(e)}")

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []

        # Validate all texts
        validated_texts = [self._validate_text(text) for text in texts]

        try:
            response = await self.client.embeddings.create(model=self.model, input=validated_texts)
            return [data.embedding for data in response.data]
        except Exception as e:
            raise RuntimeError(f"OpenAI batch embedding generation failed: {str(e)}")


class MockEmbedder(BaseEmbedder):
    """Mock embedder for testing and development"""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def get_model_name(self) -> str:
        return "mock-embedder"

    def get_embedding_dimension(self) -> int:
        return self.dimension

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate mock embedding"""
        text = self._validate_text(text)

        # Generate deterministic mock embedding based on text hash
        import hashlib

        text_hash = hashlib.md5(text.encode()).hexdigest()

        # Convert hash to numbers and normalize
        embedding = []
        for i in range(0, len(text_hash), 2):
            hex_pair = text_hash[i : i + 2]
            value = int(hex_pair, 16) / 255.0 - 0.5  # Normalize to [-0.5, 0.5]
            embedding.append(value)

        # Pad or truncate to desired dimension
        while len(embedding) < self.dimension:
            embedding.extend(embedding[: min(len(embedding), self.dimension - len(embedding))])

        return embedding[: self.dimension]

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate mock embeddings for multiple texts"""
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings


class EmbeddingService:
    """Service for managing text embeddings with different providers"""

    def __init__(self, provider: str = "openai", **kwargs):
        self.provider = provider
        self.embedder = self._create_embedder(provider, **kwargs)

    def _create_embedder(self, provider: str, **kwargs) -> BaseEmbedder:
        """Create embedder based on provider"""
        if provider == "openai":
            return OpenAIEmbedder(**kwargs)
        elif provider == "mock":
            return MockEmbedder(**kwargs)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")

    async def embed_text(self, text: str) -> Dict[str, Any]:
        """Generate embedding for a single text with metadata"""
        try:
            embedding = await self.embedder.generate_embedding(text)
            return {
                "embedding": embedding,
                "model": self.embedder.get_model_name(),
                "dimension": self.embedder.get_embedding_dimension(),
                "text_length": len(text),
                "success": True,
                "error": None,
            }
        except Exception as e:
            return {
                "embedding": None,
                "model": self.embedder.get_model_name(),
                "dimension": self.embedder.get_embedding_dimension(),
                "text_length": len(text),
                "success": False,
                "error": str(e),
            }

    async def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate embeddings for multiple chunks"""
        if not chunks:
            return []

        # Extract texts from chunks
        texts = [chunk["text"] for chunk in chunks]

        try:
            embeddings = await self.embedder.generate_embeddings(texts)

            # Add embeddings to chunks
            enriched_chunks = []
            for i, chunk in enumerate(chunks):
                enriched_chunk = chunk.copy()
                enriched_chunk.update(
                    {
                        "embedding": embeddings[i],
                        "embedding_model": self.embedder.get_model_name(),
                        "embedding_dimension": self.embedder.get_embedding_dimension(),
                        "success": True,
                        "error": None,
                    }
                )
                enriched_chunks.append(enriched_chunk)

            return enriched_chunks

        except Exception as e:
            # If batch embedding fails, try individual embeddings
            return await self._embed_chunks_individually(chunks, str(e))

    async def _embed_chunks_individually(
        self, chunks: List[Dict[str, Any]], batch_error: str
    ) -> List[Dict[str, Any]]:
        """Fallback to individual embedding generation"""
        enriched_chunks = []

        for chunk in chunks:
            try:
                embedding = await self.embedder.generate_embedding(chunk["text"])
                enriched_chunk = chunk.copy()
                enriched_chunk.update(
                    {
                        "embedding": embedding,
                        "embedding_model": self.embedder.get_model_name(),
                        "embedding_dimension": self.embedder.get_embedding_dimension(),
                        "success": True,
                        "error": None,
                    }
                )
            except Exception as e:
                enriched_chunk = chunk.copy()
                enriched_chunk.update(
                    {
                        "embedding": None,
                        "embedding_model": self.embedder.get_model_name(),
                        "embedding_dimension": self.embedder.get_embedding_dimension(),
                        "success": False,
                        "error": f"Individual embedding failed: {str(e)}",
                    }
                )

            enriched_chunks.append(enriched_chunk)

        return enriched_chunks

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "provider": self.provider,
            "model": self.embedder.get_model_name(),
            "dimension": self.embedder.get_embedding_dimension(),
        }

    async def test_connection(self) -> Dict[str, Any]:
        """Test the embedding service connection"""
        try:
            test_text = "This is a test embedding."
            result = await self.embed_text(test_text)

            return {
                "success": result["success"],
                "provider": self.provider,
                "model": self.embedder.get_model_name(),
                "dimension": self.embedder.get_embedding_dimension(),
                "error": result.get("error"),
            }
        except Exception as e:
            return {
                "success": False,
                "provider": self.provider,
                "model": self.embedder.get_model_name(),
                "dimension": self.embedder.get_embedding_dimension(),
                "error": str(e),
            }
