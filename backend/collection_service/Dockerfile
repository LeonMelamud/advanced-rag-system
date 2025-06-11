FROM collections_ai_assistance-base

# Copy backend package init to make it a proper Python package
COPY backend/__init__.py /app/backend/__init__.py

# Install collection service specific dependencies
RUN pip install --no-cache-dir \
    qdrant-client

# Copy application code maintaining directory structure
COPY backend/collection_service/__init__.py /app/backend/collection_service/__init__.py
COPY backend/collection_service/app /app/backend/collection_service/app
COPY backend/common /app/backend/common

# Set ownership and switch to non-root user
RUN chown -R app:app /app
USER app

# Standard service command (working directory already set in base)
CMD ["python", "-m", "uvicorn", "backend.collection_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 