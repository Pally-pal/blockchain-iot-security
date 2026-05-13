# Multi-stage Dockerfile for IoT Blockchain Security System
# Stage 1: Backend API Server

FROM python:3.13-slim AS api-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY src/ ./src/
COPY contracts/ ./contracts/
COPY contract_info.json .
COPY hardhat.config.js .

# Set environment variables
ENV FLASK_APP=src/api_server_complete.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose API port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health')"

# Run API server
CMD ["python", "src/api_server_complete.py"]

# Stage 2: Frontend Server

FROM python:3.13-slim AS frontend-builder

WORKDIR /app

# Copy frontend code
COPY frontend/ ./frontend/

# Set environment
ENV PYTHONUNBUFFERED=1

# Expose frontend port
EXPOSE 8000

# Run frontend server
CMD ["python", "-m", "http.server", "--directory", "frontend", "8000"]

# Stage 3: Complete Application (Multi-service)

FROM python:3.13-slim AS production

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for smart contract interaction
RUN apt-get update && apt-get install -y \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy package.json and install Node dependencies
COPY package.json package-lock.json ./
RUN npm ci --production

# Copy all application files
COPY src/ ./src/
COPY frontend/ ./frontend/
COPY contracts/ ./contracts/
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY contract_info.json hardhat.config.js ./

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV FLASK_APP=src/api_server_complete.py
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV API_HOST=0.0.0.0
ENV API_PORT=5000

# Expose ports
EXPOSE 5000 8000 8545

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Default command (runs API server)
# Use docker-compose to run both services
CMD ["python", "src/api_server_complete.py"]
