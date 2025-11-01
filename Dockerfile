# Multi-stage build for Raspberry Pi ARM64
FROM python:3.13-slim-bullseye@sha256:e98b521460ee75bca92175c16247bdf7275637a8faaeb2bcfa19d879ae5c4b9a AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    libatlas-base-dev \
    liblapack-dev \
    libopenblas-dev \
    libopencv-dev \
    pkg-config \
    python3-opencv \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create necessary directories and non-root user
RUN mkdir -p recordings markers && \
    groupadd -r poolmind && \
    useradd -r -g poolmind poolmind && \
    chown -R poolmind:poolmind /app

# Set Python path
ENV PYTHONPATH=/app/src

USER poolmind

# Expose web port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "poolmind.web.server:app", "--host", "0.0.0.0", "--port", "8000"]

# Development stage
FROM base AS development

USER root
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
USER poolmind

# Production stage
FROM base AS production

# Copy only necessary files
COPY --from=base /app /app

# Set production environment
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
