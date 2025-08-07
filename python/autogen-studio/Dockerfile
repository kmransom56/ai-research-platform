# AutoGen Studio Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager
RUN pip install uv

# Copy requirements and install dependencies
COPY pyproject.toml uv.lock* ./
RUN uv sync

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/config /app/data

# Create a non-root user
RUN useradd -m -u 1000 autogen && chown -R autogen:autogen /app
USER autogen

# Expose port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

# Start the application
CMD ["uv", "run", "autogenstudio", "ui", "--host", "0.0.0.0", "--port", "8081"]