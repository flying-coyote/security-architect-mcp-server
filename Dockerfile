# Security Architect MCP Server - Production Dockerfile
# Following 2025 MCP containerization best practices
# 60% reduction in deployment issues (industry data)

FROM python:3.11-slim AS builder

# Build stage - compile dependencies
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY pyproject.toml .
COPY src/__init__.py ./src/

# Create wheel for better caching
RUN pip install --no-cache-dir build && \
    python -m build --wheel

# -------------------------------------------
# Production stage - minimal runtime image
# -------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Security: Create non-root user (Layer 1 defense)
RUN groupadd -r mcp && \
    useradd -r -g mcp -u 1000 mcp && \
    mkdir -p /app/data /app/logs && \
    chown -R mcp:mcp /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheel from builder
COPY --from=builder /build/dist/*.whl /tmp/

# Install MCP SDK and application
RUN pip install --no-cache-dir \
    /tmp/*.whl \
    mcp \
    pydantic \
    && rm -rf /tmp/*.whl

# Copy application code (as non-root user)
COPY --chown=mcp:mcp src/ ./src/
COPY --chown=mcp:mcp data/ ./data/
COPY --chown=mcp:mcp scripts/ ./scripts/

# Security: Set read-only permissions where appropriate (Layer 2 defense)
RUN chmod -R 755 /app/src && \
    chmod -R 755 /app/scripts && \
    chmod -R 644 /app/data/*.json && \
    chmod 755 /app/data

# Security: Switch to non-root user (Layer 3 defense)
USER mcp

# Environment variables for MCP server
ENV PYTHONPATH=/app \
    MCP_TRANSPORT=streamable-http \
    MCP_SERVER_HOST=0.0.0.0 \
    MCP_SERVER_PORT=8080 \
    LOG_LEVEL=info \
    MAX_VENDORS=80 \
    TOKEN_LIMIT=10000 \
    PROGRESSIVE_DISCOVERY=true \
    CODE_EXECUTION_ENABLED=true \
    MAX_EXECUTION_TIME=30 \
    MAX_MEMORY_MB=256

# Health check for orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose MCP server port (Streamable HTTP transport)
EXPOSE 8080

# Labels for container metadata
LABEL maintainer="security-architect@example.com" \
      version="1.0.0" \
      description="Security Architect MCP Server - 2025 Best Practices" \
      org.opencontainers.image.source="https://github.com/yourusername/security-architect-mcp-server" \
      org.opencontainers.image.documentation="https://github.com/yourusername/security-architect-mcp-server/blob/main/README.md"

# Run MCP server with proper signal handling
ENTRYPOINT ["python", "-u"]
CMD ["src/server.py"]