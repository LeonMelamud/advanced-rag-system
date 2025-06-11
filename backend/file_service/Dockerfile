FROM collections_ai_assistance-base

# Install additional system dependencies for file processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Install file service specific dependencies
RUN pip install --no-cache-dir \
    qdrant-client \
    openai \
    PyMuPDF \
    pandas \
    pillow \
    pytesseract \
    aiofiles \
    python-magic

# Copy backend package init to make it a proper Python package
COPY backend/__init__.py /app/backend/__init__.py

# Copy application code maintaining directory structure
COPY backend/file_service/__init__.py /app/backend/file_service/__init__.py
COPY backend/file_service/app /app/backend/file_service/app
COPY backend/file_service/storage /app/backend/file_service/storage
COPY backend/common /app/backend/common

# Set ownership and switch to non-root user
RUN chown -R app:app /app
USER app

# Standard service command (working directory already set in base)
CMD ["python", "-m", "uvicorn", "backend.file_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]