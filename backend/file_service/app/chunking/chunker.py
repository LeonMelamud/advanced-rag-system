"""
Text Chunking Service
Implements different chunking strategies following DRY principles
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.file_service.app.models.file import ChunkingStrategy


class BaseChunker(ABC):
    """Base class for text chunkers following DRY principles"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap

    @abstractmethod
    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Chunk text and return list of chunks with metadata"""
        pass

    @abstractmethod
    def get_strategy(self) -> ChunkingStrategy:
        """Get the chunking strategy"""
        pass

    def _create_chunk(
        self,
        text: str,
        index: int,
        start_pos: int = None,
        end_pos: int = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create standardized chunk object"""
        return {
            "text": text.strip(),
            "index": index,
            "start_position": start_pos,
            "end_position": end_pos,
            "metadata": metadata or {},
        }

    def _clean_text(self, text: str) -> str:
        """Clean text by removing excessive whitespace"""
        # Replace multiple whitespace with single space
        text = re.sub(r"\s+", " ", text)
        return text.strip()


class FixedSizeChunker(BaseChunker):
    """Fixed-size chunking with overlap"""

    def get_strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.FIXED

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Chunk text into fixed-size chunks with overlap"""
        text = self._clean_text(text)
        chunks = []

        if len(text) <= self.chunk_size:
            # Text is smaller than chunk size, return as single chunk
            chunks.append(
                self._create_chunk(
                    text=text, index=0, start_pos=0, end_pos=len(text), metadata=metadata
                )
            )
            return chunks

        start = 0
        chunk_index = 0

        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))

            # Extract chunk
            chunk_text = text[start:end]

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    index=chunk_index,
                    start_pos=start,
                    end_pos=end,
                    metadata=metadata,
                )
            )

            # Move start position with overlap
            start = end - self.overlap
            chunk_index += 1

            # Prevent infinite loop if overlap is too large
            if start >= end:
                break

        return chunks


class RecursiveChunker(BaseChunker):
    """Recursive chunking that tries to split on natural boundaries"""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        super().__init__(chunk_size, overlap)
        # Define separators in order of preference
        self.separators = [
            "\n\n",  # Paragraph breaks
            "\n",  # Line breaks
            ". ",  # Sentence endings
            "! ",  # Exclamation endings
            "? ",  # Question endings
            "; ",  # Semicolon
            ", ",  # Comma
            " ",  # Space
            "",  # Character level (last resort)
        ]

    def get_strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.RECURSIVE

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Chunk text recursively using natural boundaries"""
        text = self._clean_text(text)
        return self._recursive_split(text, 0, metadata or {})

    def _recursive_split(
        self, text: str, start_offset: int = 0, metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Recursively split text using separators"""
        if len(text) <= self.chunk_size:
            return [
                self._create_chunk(
                    text=text,
                    index=0,  # Will be reindexed later
                    start_pos=start_offset,
                    end_pos=start_offset + len(text),
                    metadata=metadata,
                )
            ]

        # Try each separator
        for separator in self.separators:
            if separator in text:
                chunks = self._split_by_separator(text, separator, start_offset, metadata)
                if chunks:
                    return chunks

        # If no separator works, fall back to fixed-size chunking
        return self._fallback_split(text, start_offset, metadata)

    def _split_by_separator(
        self, text: str, separator: str, start_offset: int, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Split text by a specific separator"""
        parts = text.split(separator)
        chunks = []
        current_chunk = ""
        current_start = start_offset

        for i, part in enumerate(parts):
            # Add separator back (except for last part)
            if i < len(parts) - 1:
                part_with_sep = part + separator
            else:
                part_with_sep = part

            # Check if adding this part would exceed chunk size
            if len(current_chunk) + len(part_with_sep) <= self.chunk_size:
                current_chunk += part_with_sep
            else:
                # Save current chunk if it's not empty
                if current_chunk.strip():
                    chunks.append(
                        self._create_chunk(
                            text=current_chunk,
                            index=len(chunks),
                            start_pos=current_start,
                            end_pos=current_start + len(current_chunk),
                            metadata=metadata,
                        )
                    )

                # Start new chunk
                current_start = current_start + len(current_chunk) - self.overlap
                current_chunk = part_with_sep

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                self._create_chunk(
                    text=current_chunk,
                    index=len(chunks),
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    metadata=metadata,
                )
            )

        return chunks

    def _fallback_split(
        self, text: str, start_offset: int, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback to fixed-size splitting"""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]

            chunks.append(
                self._create_chunk(
                    text=chunk_text,
                    index=len(chunks),
                    start_pos=start_offset + start,
                    end_pos=start_offset + end,
                    metadata=metadata,
                )
            )

            start = end - self.overlap
            if start >= end:
                break

        return chunks


class ParagraphChunker(BaseChunker):
    """Paragraph-based chunking"""

    def get_strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.PARAGRAPH

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Chunk text by paragraphs, combining small ones"""
        text = self._clean_text(text)

        # Split by double newlines (paragraphs)
        paragraphs = re.split(r"\n\s*\n", text)
        chunks = []
        current_chunk = ""
        current_start = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) + 2 > self.chunk_size and current_chunk:
                # Save current chunk
                chunks.append(
                    self._create_chunk(
                        text=current_chunk,
                        index=len(chunks),
                        start_pos=current_start,
                        end_pos=current_start + len(current_chunk),
                        metadata=metadata,
                    )
                )

                # Start new chunk
                current_start = current_start + len(current_chunk)
                current_chunk = paragraph
            else:
                # Add to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add final chunk
        if current_chunk.strip():
            chunks.append(
                self._create_chunk(
                    text=current_chunk,
                    index=len(chunks),
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    metadata=metadata,
                )
            )

        return chunks


class SemanticChunker(BaseChunker):
    """Semantic chunking (placeholder for future implementation)"""

    def get_strategy(self) -> ChunkingStrategy:
        return ChunkingStrategy.SEMANTIC

    def chunk_text(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Semantic chunking - currently falls back to recursive chunking"""
        # TODO: Implement semantic chunking using sentence embeddings
        # For now, fall back to recursive chunking
        recursive_chunker = RecursiveChunker(self.chunk_size, self.overlap)
        return recursive_chunker.chunk_text(text, metadata)


class ChunkingService:
    """Service for managing text chunking with different strategies"""

    def __init__(self):
        self.chunkers = {
            ChunkingStrategy.FIXED: FixedSizeChunker,
            ChunkingStrategy.RECURSIVE: RecursiveChunker,
            ChunkingStrategy.PARAGRAPH: ParagraphChunker,
            ChunkingStrategy.SEMANTIC: SemanticChunker,
        }

    def get_chunker(
        self, strategy: ChunkingStrategy, chunk_size: int = 1000, overlap: int = 100
    ) -> BaseChunker:
        """Get chunker for specified strategy"""
        chunker_class = self.chunkers.get(strategy)
        if not chunker_class:
            raise ValueError(f"Unsupported chunking strategy: {strategy}")

        return chunker_class(chunk_size=chunk_size, overlap=overlap)

    def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE,
        chunk_size: int = 1000,
        overlap: int = 100,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Chunk text using specified strategy"""
        chunker = self.get_chunker(strategy, chunk_size, overlap)
        chunks = chunker.chunk_text(text, metadata)

        # Reindex chunks to ensure sequential numbering
        for i, chunk in enumerate(chunks):
            chunk["index"] = i

        return chunks

    def get_supported_strategies(self) -> List[ChunkingStrategy]:
        """Get list of supported chunking strategies"""
        return list(self.chunkers.keys())

    def estimate_chunks(self, text_length: int, chunk_size: int = 1000, overlap: int = 100) -> int:
        """Estimate number of chunks for given text length"""
        if text_length <= chunk_size:
            return 1

        effective_chunk_size = chunk_size - overlap
        return max(1, (text_length - overlap) // effective_chunk_size + 1)
