# Dockerfile for IoT Blockchain Security API Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Update pip to latest version to avoid dependency resolution issues
RUN pip install --upgrade pip setuptools wheel

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies with flexible version resolution
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy application files
COPY src/ ./src/
COPY contracts/ ./contracts/
COPY contract_info.json ./

# Create necessary directories
RUN mkdir -p logs results data

# Expose API port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=src/api_server_complete.py

# Health check - wait for blockchain connection
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health', timeout=5)" || exit 1

# Run the API server
CMD ["python", "src/api_server_complete.py"]
