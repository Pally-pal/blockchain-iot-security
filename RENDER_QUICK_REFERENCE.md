# Render Deployment Quick Reference

## Files Created

1. **render.yaml** - Infrastructure definition (services, ports, env vars, database)
2. **deploy-render.sh** - Bash deployment script for Linux/Mac/WSL
3. **deploy-render.ps1** - PowerShell deployment script for Windows
4. **Dockerfile.ganache** - Docker image for Ganache blockchain
5. **RENDER_DEPLOYMENT.md** - Comprehensive deployment guide

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

**Windows:**
```powershell
$env:RENDER_API_KEY = 'rnd_zU4KcmeJ8xQCCsxFgarcESq9cg7t'
.\deploy-render.ps1
```

**Linux/Mac/WSL:**
```bash
export RENDER_API_KEY='rnd_zU4KcmeJ8xQCCsxFgarcESq9cg7t'
chmod +x deploy-render.sh
./deploy-render.sh
```

### Option 2: Manual Blueprint Deployment

1. Push code to GitHub:
   ```bash
   git push origin main
   ```

2. Go to https://dashboard.render.com/blueprints

3. Click "New Blueprint Instance"

4. Connect your GitHub repository

5. Render will automatically read and apply `render.yaml`

## Deployed Services

| Service | URL | Port | Purpose |
|---------|-----|------|---------|
| Ganache | `https://iot-blockchain-ganache.onrender.com` | 8545 | Blockchain RPC |
| API | `https://iot-blockchain-api.onrender.com` | 5000 | Backend API |
| Frontend | `https://iot-blockchain-frontend.onrender.com` | 8000 | Web Interface |

## Getting Your Render API Key

1. Visit: https://dashboard.render.com/api-tokens
2. Click "Create API Token"
3. Copy the token
4. Set environment variable:
   - Windows: `$env:RENDER_API_KEY = 'token-here'`
   - Linux/Mac: `export RENDER_API_KEY='token-here'`

## Verification

After deployment:

```bash
# Check frontend
curl https://iot-blockchain-frontend.onrender.com

# Check API
curl https://iot-blockchain-api.onrender.com/api/health

# Check API docs
curl https://iot-blockchain-api.onrender.com/api/docs
```

## Environment Variables

Automatically configured:

```
FLASK_ENV=production
FLASK_APP=src/api_server_complete.py
BLOCKCHAIN_RPC_URL=http://iot-blockchain-ganache:8545
API_URL=https://iot-blockchain-api.onrender.com
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Deployment fails | Check Render Dashboard logs |
| Health check fails | Wait 2-5 min for startup, then check logs |
| API can't reach blockchain | Verify BLOCKCHAIN_RPC_URL is correct |
| Frontend can't reach API | Check CORS and API_URL settings |
| Services stuck in building | Restart in Render Dashboard |

## Important Commands

```bash
# View logs (via Render Dashboard)
Services → Select service → Logs

# Restart services
Services → Select service → Settings → Restart

# Check deployment status
https://dashboard.render.com/services

# View environment variables
Services → Select service → Environment
```

## Cost Information

- **Free Plan**: 750 hours/month, auto-suspend after 15 min inactivity
- **Paid Plans**: $7+/month for always-on services
- **Database**: $30+/month for production databases

## Next Steps

1. ✅ Deploy using script or manual blueprint
2. ✅ Verify services are running
3. ✅ Configure custom domain (optional)
4. ✅ Enable auto-deploy from GitHub
5. ✅ Set up monitoring and alerts
6. ✅ Review logs regularly

## Support Resources

- Render Docs: https://render.com/docs
- Render Support: https://support.render.com
- GitHub Issues: [Your repository]
- Project Docs: See RENDER_DEPLOYMENT.md

## Key Features of This Setup

✅ **Automated Deployment** - One command deployment
✅ **Service Orchestration** - All services managed together
✅ **Health Checks** - Automatic monitoring
✅ **Environment Variables** - Pre-configured
✅ **Database Ready** - PostgreSQL support included
✅ **Auto-Deploy** - Redeploys on GitHub push
✅ **Logging** - Comprehensive logging setup
✅ **Scaling Ready** - Easy to scale resources

---

For detailed information, see: **RENDER_DEPLOYMENT.md**
