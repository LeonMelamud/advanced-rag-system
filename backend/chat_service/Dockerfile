# Chat Service Dockerfile
FROM collections_ai_assistance-base

# Copy backend package init to make it a proper Python package
COPY backend/__init__.py /app/backend/__init__.py

# Install chat service specific dependencies
RUN pip install --no-cache-dir \
    openai \
    qdrant-client

# Copy application code maintaining directory structure
COPY backend/chat_service/__init__.py /app/backend/chat_service/__init__.py
COPY backend/chat_service/app /app/backend/chat_service/app
COPY backend/common /app/backend/common

# Set ownership and switch to non-root user
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Standard service command (working directory already set in base)
CMD ["python", "-m", "uvicorn", "backend.chat_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 