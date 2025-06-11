FROM collections_ai_assistance-base

# Copy application code maintaining directory structure
COPY backend/auth_service/__init__.py /app/backend/auth_service/__init__.py
COPY backend/auth_service/app /app/backend/auth_service/app
COPY backend/common /app/backend/common

# Set ownership and switch to non-root user
RUN chown -R app:app /app
USER app

# Standard service command (working directory already set in base)
CMD ["python", "-m", "uvicorn", "backend.auth_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"] 