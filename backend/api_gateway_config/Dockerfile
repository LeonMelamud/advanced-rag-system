FROM nginx:alpine

# Copy custom nginx configuration
COPY backend/api_gateway_config/nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 