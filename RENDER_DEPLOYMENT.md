# Render Deployment Guide

This guide explains how to deploy the IoT Blockchain Security System to [Render.com](https://render.com).

## Overview

The deployment includes three services:
- **Ganache**: Blockchain simulator (port 8545)
- **API Server**: Flask backend (port 5000)
- **Frontend**: Web interface (port 8000)

## Prerequisites

- Render account with API key
- GitHub repository connected to Render
- Docker installed locally
- Git installed locally

## Quick Start

### Step 1: Get Your Render API Key

1. Go to [https://dashboard.render.com/api-tokens](https://dashboard.render.com/api-tokens)
2. Create a new API token
3. Set environment variable:

**Windows (PowerShell):**
```powershell
$env:RENDER_API_KEY = 'rnd_zU4KcmeJ8xQCCsxFgarcESq9cg7t'
```

**Linux/Mac/WSL:**
```bash
export RENDER_API_KEY='rnd_zU4KcmeJ8xQCCsxFgarcESq9cg7t'
```

### Step 2: Run the Deployment Script

**Windows (PowerShell):**
```powershell
.\deploy-render.ps1
```

With options:
```powershell
.\deploy-render.ps1 -SkipBuild -SkipHealthCheck
.\deploy-render.ps1 -DryRun  # Preview without making changes
```

**Linux/Mac/WSL:**
```bash
chmod +x deploy-render.sh
./deploy-render.sh
```

### Step 3: Manual Deployment (Alternative)

If you prefer to deploy manually:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Render"
   git push origin main
   ```

2. **Create Blueprint in Render:**
   - Go to [https://dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)
   - Click "New Blueprint Instance"
   - Connect your GitHub repository
   - Use the `render.yaml` configuration

## Files Included

### 1. **render.yaml**
Infrastructure as Code file that defines:
- Service configurations (Ganache, API, Frontend)
- Port mappings
- Environment variables
- Health checks
- Dependencies between services
- Database setup (PostgreSQL)

### 2. **deploy-render.sh**
Bash script for Linux/Mac/WSL that:
- Checks prerequisites (Docker, Git, API key)
- Builds Docker images
- Commits and pushes to GitHub
- Configures environment variables
- Runs health checks
- Provides deployment summary

Usage:
```bash
./deploy-render.sh
```

### 3. **deploy-render.ps1**
PowerShell script for Windows that provides the same functionality as the bash script.

Usage:
```powershell
.\deploy-render.ps1 [options]
```

Options:
- `-SkipBuild`: Skip Docker image building
- `-SkipHealthCheck`: Skip health checks after deployment
- `-DryRun`: Preview deployment without making changes

## Environment Variables

The following environment variables are automatically configured:

| Variable | Value | Service |
|----------|-------|---------|
| `FLASK_ENV` | `production` | API |
| `FLASK_APP` | `src/api_server_complete.py` | API |
| `BLOCKCHAIN_RPC_URL` | `http://iot-blockchain-ganache:8545` | API |
| `API_URL` | `https://iot-blockchain-api.onrender.com` | Frontend |
| `LOG_LEVEL` | `INFO` | API |
| `PYTHONUNBUFFERED` | `1` | All |

## Deployment URLs

After successful deployment:

- **Frontend:** `https://iot-blockchain-frontend.onrender.com`
- **API:** `https://iot-blockchain-api.onrender.com`
- **API Docs:** `https://iot-blockchain-api.onrender.com/api/docs`
- **Blockchain RPC:** `https://iot-blockchain-ganache.onrender.com:8545`
- **Dashboard:** `https://dashboard.render.com`

## Monitoring

### View Logs
```bash
# Via Render Dashboard
1. Go to https://dashboard.render.com
2. Select service
3. Click "Logs"

# Via Render CLI (if installed)
render logs <service-id>
```

### Check Service Status
```bash
curl https://iot-blockchain-api.onrender.com/api/health
```

### Restart Services
1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Select service
3. Click "Restart"

## Troubleshooting

### Service Won't Start
1. Check logs in Render Dashboard
2. Verify environment variables are set correctly
3. Ensure Docker images build locally
4. Check service dependencies in render.yaml

### Health Check Fails
1. Wait longer for services to initialize (up to 5 minutes)
2. Check API logs for errors
3. Verify network connectivity between services
4. Check database connection strings

### API Can't Connect to Blockchain
1. Verify `BLOCKCHAIN_RPC_URL` environment variable
2. Check Ganache service is running
3. Check Ganache logs in Render Dashboard
4. Verify port 8545 is accessible

### Frontend Can't Connect to API
1. Verify `API_URL` environment variable
2. Check CORS headers in API
3. Verify API service is running
4. Check frontend logs in browser console

## Scaling and Configuration

### Increase Resources
In `render.yaml`, change `plan` from `standard` to:
- `starter`: Limited resources, free tier
- `standard`: 2 CPU, 8GB RAM
- `pro`: 4 CPU, 16GB RAM

### Database Configuration
Uncomment and configure the database section in `render.yaml`:
```yaml
databases:
  - name: iot-blockchain-postgres
    databaseName: iot_blockchain_db
    user: iot_user
    region: ohio
    plan: standard
```

Update your API connection string in environment variables.

## CI/CD and Auto-Deployment

### Enable GitHub Integration
1. Go to [https://dashboard.render.com](https://dashboard.render.com)
2. Click "Services" → Select service
3. Click "Settings" → "Deploy Hook"
4. Copy the hook URL
5. Add to GitHub Actions or webhooks

### Automatic Deployment on Push
The `render.yaml` includes `autoDeploy: true` for all services, which automatically redeploys when you push to the connected GitHub branch.

## Cost Considerations

**Free Tier:**
- Up to 3 services
- 750 free hours/month
- Automatic suspend after 15 min inactivity
- Shared CPU

**Paid Plans:**
- Dedicated resources
- No auto-suspend
- Higher performance

## Cleanup

To remove all services from Render:
```bash
# Via Render Dashboard
1. Go to Services
2. Select each service
3. Click Settings → Delete Service

# Delete database (if created)
1. Go to Databases
2. Select database
3. Click Delete
```

## Support

For issues specific to Render:
- Render Docs: https://render.com/docs
- Render Support: https://support.render.com

For issues with the project:
- GitHub Issues: [Your repository]
- Author: Oyelade Paul Oluwafemi

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit API keys** - Always use environment variables
2. **Secure your database** - Use strong passwords
3. **Enable HTTPS** - Render provides free SSL certificates
4. **Rotate credentials regularly** - Update API keys and passwords
5. **Monitor logs** - Check for suspicious activity
6. **Use private repositories** - For sensitive code
7. **Environment-specific configs** - Different settings for prod/dev

## Advanced: Custom Domain

To use a custom domain:

1. In Render Dashboard, go to service settings
2. Click "Add Custom Domain"
3. Add DNS records as instructed
4. Wait for SSL certificate (5-10 minutes)

Example:
```
api.yourdomain.com → iot-blockchain-api.onrender.com
app.yourdomain.com → iot-blockchain-frontend.onrender.com
```

## Advanced: Database Backup

To backup your database:

1. Go to [https://dashboard.render.com/databases](https://dashboard.render.com/databases)
2. Select database
3. Click "Backups" → "Create Manual Backup"
4. Download backup when ready

## Rollback

If deployment fails:

1. Go to Render Dashboard
2. Select service
3. Click "Deployments" tab
4. Find previous successful deployment
5. Click "Redeploy"

Or use the Render CLI:
```bash
render redeploy <service-id> --commit <commit-hash>
```

---

**Last Updated:** 2026-05-13
**Project:** IoT Blockchain Security System
