# Deployment Guide - IoT Blockchain Security System

This guide explains how to deploy and run the complete system (Frontend, API, and Blockchain).

## Table of Contents
1. [Docker Deployment (Recommended)](#docker-deployment)
2. [Local Development](#local-development)
3. [Production Deployment](#production-deployment)
4. [Troubleshooting](#troubleshooting)

---

## Docker Deployment (Recommended)

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space

### Quick Start with Docker

#### 1. Clone and Navigate to Project
```bash
cd blockchain-iot-security
```

#### 2. Build Docker Images
```bash
# Build all services
docker-compose build

# Or build specific services
docker-compose build api frontend ganache
```

#### 3. Start All Services
```bash
# Start services in background
docker-compose up -d

# Or run in foreground to see logs
docker-compose up
```

#### 4. Verify Services
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f ganache
```

#### 5. Access the System
- **Frontend:** http://localhost:8000
- **API:** http://localhost:5000
- **API Docs:** http://localhost:5000/api/docs
- **Blockchain (Ganache):** http://localhost:8545

#### 6. Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Compose Services

**Service 1: Ganache (Blockchain)**
- Image: `trufflesuite/ganache:latest`
- Port: 8545
- Volume: `ganache_data:/ganache_data` (persistent blockchain data)
- Auto-generates 10 Ethereum accounts with 100 ETH each
- Deterministic mode for reproducibility

**Service 2: API Server**
- Dockerfile: `Dockerfile.api`
- Port: 5000
- Dependencies: Ganache
- Health Check: Every 30s
- Environment: Production mode

**Service 3: Frontend**
- Dockerfile: `Dockerfile.frontend`
- Port: 8000
- Dependencies: API Server
- Health Check: Every 30s
- Serves on Python HTTP server

### Docker Environment Variables

Create `.env` file for custom configuration:

```env
# Blockchain
GANACHE_URL=http://ganache:8545
NETWORK_ID=1337

# API
API_HOST=0.0.0.0
API_PORT=5000
API_HOST_EXTERNAL=http://localhost:5000
FLASK_ENV=production

# Frontend
FRONTEND_PORT=8000
FRONTEND_HOST=0.0.0.0
```

### Scaling Docker Services

```bash
# Scale API instances behind a load balancer
docker-compose up -d --scale api=3

# Scale frontend instances
docker-compose up -d --scale frontend=2
```

### Docker Network

Services communicate via `iot-blockchain-network`:
- `ganache:8545` - Blockchain endpoint
- `api:5000` - API server
- `frontend:8000` - Frontend server

All services can resolve each other by hostname within the container network.

---

## Local Development

### Quick Start

### Option 1: Direct Browser Access (File Protocol)

1. Open the frontend folder in your file system
2. Double-click `index.html` to open in browser
3. Go to Settings and configure API URL:
   - Host: `http://localhost`
   - Port: `5000` (or your API port)
4. Start using the frontend

**Limitations:**
- File protocol (file://) may have CORS restrictions
- Not ideal for production
- Refresh may not work smoothly

### Option 2: Python HTTP Server (Recommended)

#### Windows
```powershell
# Navigate to frontend directory
cd .\frontend

# Run serve.py
python serve.py

# Or use built-in HTTP server
python -m http.server 8000
```

#### macOS/Linux
```bash
# Navigate to frontend directory
cd ./frontend

# Run serve.py
python3 serve.py

# Or use built-in HTTP server
python3 -m http.server 8000
```

Then open: `http://localhost:8000`

### Option 3: Node.js HTTP Server

```bash
# If you have http-server installed
npm install -g http-server

# Navigate to frontend directory
cd ./frontend

# Start server
http-server -p 8000
```

### Option 4: Integration with Existing Flask API

Modify your API server to serve the frontend directly:

```python
# In api_server_complete.py, add after app initialization:

from flask import send_from_directory, render_template_string

# Serve frontend files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('frontend', filename)

@app.route('/frontend')
@app.route('/frontend/')
def serve_frontend():
    with open('frontend/index.html', 'r') as f:
        return f.read()

@app.route('/frontend/<path:filename>')
def frontend_static(filename):
    try:
        return send_from_directory('frontend', filename)
    except FileNotFoundError:
        return send_from_directory('frontend', 'index.html')
```

Then access: `http://localhost:5000/frontend`

## Production Deployment

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/iot-blockchain/frontend;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:5000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache Configuration

```apache
<VirtualHost *:80>
    ServerName your-domain.com
    DocumentRoot /var/www/iot-blockchain/frontend

    # Frontend
    <Directory /var/www/iot-blockchain/frontend>
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>

    # API proxy
    ProxyPass /api/ http://localhost:5000/api/
    ProxyPassReverse /api/ http://localhost:5000/api/
</VirtualHost>
```

### Docker Deployment

#### Dockerfile for Frontend + API

```dockerfile
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/ .
RUN npm install -g http-server

FROM python:3.11-slim
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY contracts/ ./contracts/
COPY artifacts/ ./artifacts/
COPY frontend/ ./frontend/

# Expose ports
EXPOSE 5000 8000

# Start both servers
CMD ["sh", "-c", "python src/api_server_complete.py & cd frontend && http-server -p 8000 --gzip"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GANACHE_URL=http://ganache:8545
    depends_on:
      - ganache

  frontend:
    image: node:18-alpine
    working_dir: /app
    volumes:
      - ./frontend:/app
    ports:
      - "8000:8000"
    command: sh -c "npm install -g http-server && http-server -p 8000 --gzip"

  ganache:
    image: trufflesuite/ganache:latest
    ports:
      - "8545:8545"
```

## API Configuration

The frontend needs to communicate with your API. Configure the API setting:

### In Browser Settings
1. Click ⚙️ Settings button
2. Set API Host: `http://yourdomain.com` (or localhost)
3. Set API Port: `5000` (or your API port)
4. Click Save

### Environment Variable (Future Enhancement)
Create `.env` file:
```
VITE_API_URL=http://localhost:5000
```

## CORS Configuration

Ensure your API has CORS enabled:

```python
# In api_server_complete.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": ["http://localhost:8000", "http://localhost:5000"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type"]
}})
```

## Security Considerations

### For Production:

1. **HTTPS/TLS**
   - Always use HTTPS in production
   - Use Let's Encrypt for free SSL certificates
   - Update API URLs to use `https://`

2. **CORS**
   - Restrict CORS to specific origins
   - Don't use wildcard (`*`) in production

3. **API Authentication**
   - Add API key validation
   - Implement JWT tokens
   - Rate limiting

4. **Frontend Security**
   - Minify and optimize assets
   - Use Content Security Policy (CSP)
   - Regular security audits

5. **Environment Variables**
   - Never hardcode API URLs
   - Use environment variables
   - Rotate secrets regularly

### Example Security Headers

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

## Troubleshooting

### Frontend not connecting to API

1. Check if API server is running:
   ```bash
   curl http://localhost:5000/api/health
   ```

2. Check browser console for CORS errors (F12)

3. Verify API URL in settings matches your configuration

4. Check network tab in browser dev tools

### CORS Errors

```
Access to XMLHttpRequest blocked by CORS policy
```

Solution: Ensure CORS is enabled on API server

### Port Already in Use

```
Address already in use
```

Solution: Change port in serve.py or use:
```bash
python -m http.server 8001  # Use different port
```

### Static Files Not Loading

Clear browser cache (Ctrl+Shift+Delete) and retry

### Blockchain Connection Issues

Ensure Ganache is running:
```bash
ganache-cli
```

## Performance Optimization

1. **Compress Assets**
   ```bash
   gzip index.html styles.css app.js
   ```

2. **Minify Files**
   - Use minifiers for CSS and JavaScript
   - Reduce file sizes

3. **Caching**
   - Configure browser caching headers
   - Use CDN for static assets

4. **Lazy Loading**
   - Load data on demand
   - Pagination for large datasets

## Monitoring

Monitor deployment health:

```bash
# Check API health
curl http://localhost:5000/api/health

# Check frontend availability
curl http://localhost:8000

# Monitor logs
tail -f logs/api.log
tail -f logs/frontend.log
```

## Backup and Recovery

1. **Backup frontend files**
   ```bash
   tar -czf frontend-backup.tar.gz frontend/
   ```

2. **Backup database and blockchain data**
   ```bash
   tar -czf blockchain-backup.tar.gz data/ artifacts/
   ```

3. **Version control**
   ```bash
   git commit -m "Frontend deployment"
   git push
   ```

## Next Steps

1. Test all frontend features
2. Verify API connectivity
3. Run security audit
4. Set up monitoring
5. Plan scaling strategy
6. Document deployment process
7. Create backup schedule
