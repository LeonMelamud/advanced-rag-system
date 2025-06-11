"""
Text Extraction Processors
Handles text extraction from different file types following DRY principles
"""

import io
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import fitz  # PyMuPDF
import pandas as pd

from backend.file_service.app.models.file import FileType


class BaseTextExtractor(ABC):
    """Base class for text extractors following DRY principles"""

    @abstractmethod
    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from file and return metadata"""
        pass

    @abstractmethod
    def supports_file_type(self, file_type: FileType) -> bool:
        """Check if extractor supports the file type"""
        pass

    def _create_extraction_result(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized extraction result"""
        return {
            "text": text,
            "text_length": len(text),
            "metadata": metadata or {},
            "success": True,
            "error": None,
        }

    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create standardized error result"""
        return {
            "text": "",
            "text_length": 0,
            "metadata": {},
            "success": False,
            "error": error_message,
        }


class PDFTextExtractor(BaseTextExtractor):
    """PDF text extraction using PyMuPDF"""

    def supports_file_type(self, file_type: FileType) -> bool:
        return file_type == FileType.PDF

    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF file"""
        try:
            doc = fitz.open(file_path)
            text_parts = []
            metadata = {"page_count": len(doc), "pages": []}

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                page_text = page.get_text()

                if page_text.strip():  # Only add non-empty pages
                    text_parts.append(page_text)
                    metadata["pages"].append(
                        {
                            "page_number": page_num + 1,
                            "text_length": len(page_text),
                            "has_images": len(page.get_images()) > 0,
                        }
                    )

            doc.close()

            full_text = "\n\n".join(text_parts)
            metadata["extraction_method"] = "pymupdf"
            metadata["total_text_length"] = len(full_text)

            return self._create_extraction_result(full_text, metadata)

        except Exception as e:
            return self._create_error_result(f"PDF extraction failed: {str(e)}")


class CSVTextExtractor(BaseTextExtractor):
    """CSV text extraction using pandas"""

    def supports_file_type(self, file_type: FileType) -> bool:
        return file_type == FileType.CSV

    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from CSV file"""
        try:
            # Try different encodings
            encodings = ["utf-8", "latin-1", "cp1252"]
            df = None
            used_encoding = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                return self._create_error_result(
                    "Could not decode CSV file with any supported encoding"
                )

            # Convert DataFrame to text representation
            text_parts = []

            # Add column headers
            headers = " | ".join(df.columns.astype(str))
            text_parts.append(f"Headers: {headers}")

            # Add data rows
            for index, row in df.iterrows():
                row_text = " | ".join(row.astype(str))
                text_parts.append(f"Row {index + 1}: {row_text}")

            full_text = "\n".join(text_parts)

            metadata = {
                "row_count": len(df),
                "column_count": len(df.columns),
                "columns": df.columns.tolist(),
                "encoding": used_encoding,
                "extraction_method": "pandas",
                "data_types": df.dtypes.astype(str).to_dict(),
            }

            return self._create_extraction_result(full_text, metadata)

        except Exception as e:
            return self._create_error_result(f"CSV extraction failed: {str(e)}")


class TXTTextExtractor(BaseTextExtractor):
    """Plain text file extraction"""

    def supports_file_type(self, file_type: FileType) -> bool:
        return file_type in [FileType.TXT, FileType.MD]

    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from plain text file"""
        try:
            # Try different encodings
            encodings = ["utf-8", "latin-1", "cp1252"]
            text = None
            used_encoding = None

            for encoding in encodings:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        text = f.read()
                    used_encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue

            if text is None:
                return self._create_error_result(
                    "Could not decode text file with any supported encoding"
                )

            # Count lines and words
            lines = text.split("\n")
            words = text.split()

            metadata = {
                "line_count": len(lines),
                "word_count": len(words),
                "encoding": used_encoding,
                "extraction_method": "direct_read",
            }

            return self._create_extraction_result(text, metadata)

        except Exception as e:
            return self._create_error_result(f"Text extraction failed: {str(e)}")


class AudioTextExtractor(BaseTextExtractor):
    """Audio transcription (placeholder for future Whisper integration)"""

    def supports_file_type(self, file_type: FileType) -> bool:
        return file_type == FileType.AUDIO

    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from audio file using transcription"""
        # TODO: Implement Whisper integration
        # For now, return a placeholder
        return self._create_error_result("Audio transcription not yet implemented")


class DOCXTextExtractor(BaseTextExtractor):
    """DOCX text extraction (placeholder for future implementation)"""

    def supports_file_type(self, file_type: FileType) -> bool:
        return file_type == FileType.DOCX

    async def extract_text(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX file"""
        # TODO: Implement python-docx integration
        # For now, return a placeholder
        return self._create_error_result("DOCX extraction not yet implemented")


class TextExtractionService:
    """Service for managing text extraction from different file types"""

    def __init__(self):
        self.extractors = [
            PDFTextExtractor(),
            CSVTextExtractor(),
            TXTTextExtractor(),
            AudioTextExtractor(),
            DOCXTextExtractor(),
        ]

    def get_extractor(self, file_type: FileType) -> Optional[BaseTextExtractor]:
        """Get appropriate extractor for file type"""
        for extractor in self.extractors:
            if extractor.supports_file_type(file_type):
                return extractor
        return None

    async def extract_text(self, file_path: str, file_type: FileType) -> Dict[str, Any]:
        """Extract text from file using appropriate extractor"""
        extractor = self.get_extractor(file_type)

        if not extractor:
            return {
                "text": "",
                "text_length": 0,
                "metadata": {},
                "success": False,
                "error": f"No extractor available for file type: {file_type}",
            }

        # Verify file exists
        if not os.path.exists(file_path):
            return {
                "text": "",
                "text_length": 0,
                "metadata": {},
                "success": False,
                "error": f"File not found: {file_path}",
            }

        return await extractor.extract_text(file_path)

    def get_supported_file_types(self) -> list[FileType]:
        """Get list of supported file types"""
        supported_types = []
        for file_type in FileType:
            if self.get_extractor(file_type):
                supported_types.append(file_type)
        return supported_types
