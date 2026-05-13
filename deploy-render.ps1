# PowerShell Deployment Script for Render
# Render Deployment Script for IoT Blockchain Security System
# This script automates the deployment to Render.com

param(
    [switch]$SkipBuild = $false,
    [switch]$SkipHealthCheck = $false,
    [switch]$DryRun = $false
)

# Configuration
$PROJECT_NAME = "iot-blockchain-security"
$RENDER_API_KEY = $env:RENDER_API_KEY
$GITHUB_REPO = $env:GITHUB_REPO
$REGION = "ohio"
$PLAN = "standard"
$SERVICES = @("iot-blockchain-ganache", "iot-blockchain-api", "iot-blockchain-frontend")

# Color functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

##############################################################################
# Check Prerequisites
##############################################################################

function Check-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check for Docker
    $dockerCheck = docker --version 2>$null
    if (-not $dockerCheck) {
        Write-Error "Docker is required but not installed"
        exit 1
    }
    Write-Success "Docker found: $dockerCheck"
    
    # Check for Git
    $gitCheck = git --version 2>$null
    if (-not $gitCheck) {
        Write-Error "Git is required but not installed"
        exit 1
    }
    Write-Success "Git found"
    
    # Check for Render API key
    if (-not $RENDER_API_KEY) {
        Write-Error "RENDER_API_KEY environment variable not set"
        Write-Host "Please set your Render API key:" -ForegroundColor Yellow
        Write-Host "`$env:RENDER_API_KEY = 'your-api-key-here'"
        exit 1
    }
    Write-Success "Render API key configured"
    
    Write-Success "All prerequisites met`n"
}

##############################################################################
# Build Docker Images
##############################################################################

function Build-DockerImages {
    Write-Info "Building Docker images..."
    
    try {
        Write-Info "Building Ganache image..."
        docker build -f Dockerfile.ganache -t "${PROJECT_NAME}-ganache:latest" . | Out-Null
        Write-Success "Ganache image built"
        
        Write-Info "Building API image..."
        docker build -f Dockerfile.api -t "${PROJECT_NAME}-api:latest" . | Out-Null
        Write-Success "API image built"
        
        Write-Info "Building Frontend image..."
        docker build -f Dockerfile.frontend -t "${PROJECT_NAME}-frontend:latest" . | Out-Null
        Write-Success "Frontend image built`n"
    }
    catch {
        Write-Error "Failed to build Docker images: $_"
        exit 1
    }
}

##############################################################################
# Git Workflow
##############################################################################

function Git-PushAndDeploy {
    Write-Info "Preparing git for deployment..."
    
    try {
        # Check git status
        $status = git status --porcelain
        if ($status) {
            Write-Warning "Working directory has uncommitted changes"
            $confirm = Read-Host "Commit and push changes? (y/n)"
            if ($confirm -eq "y") {
                git add .
                git commit -m "Deploy: Render deployment updates"
                Write-Success "Changes committed"
            }
            else {
                Write-Warning "Skipping git commit"
                return $false
            }
        }
        else {
            Write-Info "Working directory is clean"
        }
        
        # Get current branch
        $branch = git rev-parse --abbrev-ref HEAD
        Write-Info "Pushing branch: $branch"
        git push origin $branch
        Write-Success "Changes pushed successfully`n"
        return $true
    }
    catch {
        Write-Error "Git operation failed: $_"
        return $false
    }
}

##############################################################################
# Set Environment Variables
##############################################################################

function Set-EnvironmentVariables {
    Write-Info "Configuring environment variables..."
    
    $envVars = @{
        "FLASK_ENV" = "production"
        "FLASK_APP" = "src/api_server_complete.py"
        "BLOCKCHAIN_RPC_URL" = "http://iot-blockchain-ganache:8545"
        "API_URL" = "https://iot-blockchain-api.onrender.com"
        "LOG_LEVEL" = "INFO"
        "PYTHONUNBUFFERED" = "1"
    }
    
    foreach ($key in $envVars.Keys) {
        Write-Info "Setting: $key = $($envVars[$key])"
    }
    
    Write-Success "Environment variables configured`n"
}

##############################################################################
# Health Checks
##############################################################################

function Check-DeploymentHealth {
    if ($SkipHealthCheck) {
        Write-Warning "Skipping health checks"
        return $true
    }
    
    Write-Info "Checking deployment health..."
    
    $maxAttempts = 30
    $attempt = 0
    $apiUrl = "https://iot-blockchain-api.onrender.com/api/health"
    $frontendUrl = "https://iot-blockchain-frontend.onrender.com"
    
    while ($attempt -lt $maxAttempts) {
        Write-Info "Health check attempt $($attempt + 1)/$maxAttempts"
        
        try {
            $apiResponse = Invoke-WebRequest -Uri $apiUrl -ErrorAction SilentlyContinue
            $apiStatus = $apiResponse.StatusCode
        }
        catch {
            $apiStatus = "000"
        }
        
        try {
            $frontendResponse = Invoke-WebRequest -Uri $frontendUrl -ErrorAction SilentlyContinue
            $frontendStatus = $frontendResponse.StatusCode
        }
        catch {
            $frontendStatus = "000"
        }
        
        if ($apiStatus -eq 200 -and $frontendStatus -eq 200) {
            Write-Success "All services are healthy`n"
            return $true
        }
        
        Write-Warning "API Status: $apiStatus, Frontend Status: $frontendStatus"
        Start-Sleep -Seconds 10
        $attempt++
    }
    
    Write-Error "Deployment health check failed after $maxAttempts attempts"
    return $false
}

##############################################################################
# Deployment Summary
##############################################################################

function Print-DeploymentSummary {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║          Deployment Complete - Service URLs                   ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Frontend:  " -ForegroundColor Cyan -NoNewline
    Write-Host "https://iot-blockchain-frontend.onrender.com"
    Write-Host "API:       " -ForegroundColor Cyan -NoNewline
    Write-Host "https://iot-blockchain-api.onrender.com"
    Write-Host "API Docs:  " -ForegroundColor Cyan -NoNewline
    Write-Host "https://iot-blockchain-api.onrender.com/api/docs"
    Write-Host "Blockchain:" -ForegroundColor Cyan -NoNewline
    Write-Host " https://iot-blockchain-ganache.onrender.com (port 8545)"
    Write-Host ""
    Write-Host "Dashboard: " -ForegroundColor Cyan -NoNewline
    Write-Host "https://dashboard.render.com"
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Monitor deployments: https://dashboard.render.com"
    Write-Host "2. View logs: Use Render Dashboard"
    Write-Host "3. Configure custom domain: https://dashboard.render.com/services"
    Write-Host "4. Set up automatic deployments: Connect GitHub repository"
    Write-Host ""
}

##############################################################################
# Main Deployment Flow
##############################################################################

function Main {
    Write-Host ""
    Write-Info "Starting Render deployment for $PROJECT_NAME`n"
    
    # Step 1: Check prerequisites
    Check-Prerequisites
    
    # Step 2: Show dry-run status
    if ($DryRun) {
        Write-Warning "Running in DRY RUN mode - no changes will be made`n"
    }
    
    # Step 3: Confirm deployment
    Write-Warning "This will deploy to Render.com"
    $confirm = Read-Host "Continue with deployment? (y/n)"
    if ($confirm -ne "y") {
        Write-Info "Deployment cancelled"
        exit 0
    }
    Write-Host ""
    
    # Step 4: Build Docker images (optional)
    if (-not $SkipBuild) {
        $buildConfirm = Read-Host "Build Docker images? (y/n)"
        if ($buildConfirm -eq "y") {
            Build-DockerImages
        }
    }
    
    # Step 5: Git push
    if (-not $DryRun) {
        if (-not (Git-PushAndDeploy)) {
            exit 1
        }
    }
    else {
        Write-Warning "[DRY RUN] Would push to Git repository"
    }
    
    # Step 6: Set environment variables
    Set-EnvironmentVariables
    
    # Step 7: Health checks (optional)
    if (-not $SkipHealthCheck) {
        $healthCheck = Read-Host "Run health checks? (y/n)"
        if ($healthCheck -eq "y") {
            Write-Info "Waiting 30 seconds for services to start..."
            Start-Sleep -Seconds 30
            Check-DeploymentHealth
        }
    }
    
    # Print summary
    Print-DeploymentSummary
    
    Write-Success "Deployment process completed!"
}

# Run main function
Main
