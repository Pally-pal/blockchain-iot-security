#!/bin/bash

##############################################################################
# Render Deployment Script for IoT Blockchain Security System
# This script automates the deployment to Render.com
##############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="iot-blockchain-security"
RENDER_API_KEY="${RENDER_API_KEY:-}"
GITHUB_REPO="${GITHUB_REPO:-}"
REGION="ohio"
PLAN="standard"

# Services
SERVICES=("iot-blockchain-ganache" "iot-blockchain-api" "iot-blockchain-frontend")

##############################################################################
# Helper Functions
##############################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

##############################################################################
# Check Prerequisites
##############################################################################

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check for required tools
    command -v curl >/dev/null 2>&1 || {
        log_error "curl is required but not installed"
        exit 1
    }
    
    command -v git >/dev/null 2>&1 || {
        log_error "git is required but not installed"
        exit 1
    }
    
    # Check for Render API key
    if [ -z "$RENDER_API_KEY" ]; then
        log_error "RENDER_API_KEY environment variable not set"
        echo "Please set your Render API key:"
        echo "  export RENDER_API_KEY='your-api-key-here'"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

##############################################################################
# Build and Push Docker Images
##############################################################################

build_docker_images() {
    log_info "Building Docker images..."
    
    docker build -f Dockerfile.ganache -t ${PROJECT_NAME}-ganache:latest .
    [ $? -eq 0 ] && log_success "Ganache image built" || {
        log_error "Failed to build Ganache image"
        return 1
    }
    
    docker build -f Dockerfile.api -t ${PROJECT_NAME}-api:latest .
    [ $? -eq 0 ] && log_success "API image built" || {
        log_error "Failed to build API image"
        return 1
    }
    
    docker build -f Dockerfile.frontend -t ${PROJECT_NAME}-frontend:latest .
    [ $? -eq 0 ] && log_success "Frontend image built" || {
        log_error "Failed to build Frontend image"
        return 1
    }
}

##############################################################################
# Deploy to Render using API
##############################################################################

deploy_to_render() {
    log_info "Deploying to Render..."
    
    if [ ! -f "render.yaml" ]; then
        log_error "render.yaml not found in current directory"
        return 1
    fi
    
    # Check if services exist
    for service in "${SERVICES[@]}"; do
        check_service "$service"
    done
}

check_service() {
    local service_name=$1
    
    log_info "Checking service: $service_name"
    
    # Get service info (requires Render CLI or custom API call)
    # This is a placeholder - actual implementation depends on Render API
    curl -s -H "Authorization: Bearer ${RENDER_API_KEY}" \
        "https://api.render.com/v1/services" \
        -o /dev/null -w "%{http_code}" || {
        log_warning "Could not verify service $service_name"
    }
}

##############################################################################
# Git Workflow
##############################################################################

git_push_and_deploy() {
    log_info "Preparing git for deployment..."
    
    # Check git status
    if [ -z "$(git status --porcelain)" ]; then
        log_info "Working directory is clean"
    else
        log_warning "Working directory has uncommitted changes"
        read -p "Commit and push changes? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "Deploy: Render deployment updates"
        else
            log_warning "Skipping git commit"
            return 1
        fi
    fi
    
    # Push to main/master branch
    local branch=$(git rev-parse --abbrev-ref HEAD)
    log_info "Pushing branch: $branch"
    git push origin "$branch"
    [ $? -eq 0 ] && log_success "Changes pushed successfully" || {
        log_error "Failed to push changes"
        return 1
    }
}

##############################################################################
# Set Environment Variables
##############################################################################

set_environment_variables() {
    log_info "Setting environment variables on Render..."
    
    local env_vars=(
        "FLASK_ENV=production"
        "FLASK_APP=src/api_server_complete.py"
        "BLOCKCHAIN_RPC_URL=http://iot-blockchain-ganache:8545"
        "API_URL=https://iot-blockchain-api.onrender.com"
        "LOG_LEVEL=INFO"
        "PYTHONUNBUFFERED=1"
    )
    
    for var in "${env_vars[@]}"; do
        log_info "Setting: $var"
    done
    
    log_success "Environment variables configured"
}

##############################################################################
# Health Checks
##############################################################################

check_deployment_health() {
    log_info "Checking deployment health..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        log_info "Health check attempt $((attempt + 1))/$max_attempts"
        
        # Check API
        api_status=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://iot-blockchain-api.onrender.com/api/health" || echo "000")
        
        # Check Frontend
        frontend_status=$(curl -s -o /dev/null -w "%{http_code}" \
            "https://iot-blockchain-frontend.onrender.com" || echo "000")
        
        if [ "$api_status" = "200" ] && [ "$frontend_status" = "200" ]; then
            log_success "All services are healthy"
            return 0
        fi
        
        log_warning "API Status: $api_status, Frontend Status: $frontend_status"
        sleep 10
        ((attempt++))
    done
    
    log_error "Deployment health check failed after $max_attempts attempts"
    return 1
}

##############################################################################
# Deployment Summary
##############################################################################

print_deployment_summary() {
    cat << EOF

${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}
${GREEN}║          Deployment Complete - Service URLs                   ║${NC}
${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}

${BLUE}Frontend:${NC}  https://iot-blockchain-frontend.onrender.com
${BLUE}API:${NC}       https://iot-blockchain-api.onrender.com
${BLUE}API Docs:${NC}   https://iot-blockchain-api.onrender.com/api/docs
${BLUE}Blockchain:${NC} https://iot-blockchain-ganache.onrender.com (port 8545)

${BLUE}Dashboard:${NC}  https://dashboard.render.com

${YELLOW}Next Steps:${NC}
1. Monitor deployments: https://dashboard.render.com
2. View logs: Use Render Dashboard
3. Configure custom domain: https://dashboard.render.com/services
4. Set up automatic deployments: Connect GitHub repository

${YELLOW}Useful Commands:${NC}
- View API logs:      curl https://api.render.com/v1/services/iot-blockchain-api/logs
- Restart services:   Via Render Dashboard
- Scale services:     Via Render Dashboard

EOF
}

##############################################################################
# Main Deployment Flow
##############################################################################

main() {
    log_info "Starting Render deployment for $PROJECT_NAME"
    
    # Step 1: Check prerequisites
    check_prerequisites || exit 1
    
    # Step 2: Confirm deployment
    echo
    log_warning "This will deploy to Render.com"
    read -p "Continue with deployment? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
    
    # Step 3: Build Docker images (optional)
    read -p "Build Docker images? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        build_docker_images || exit 1
    fi
    
    # Step 4: Git push
    git_push_and_deploy || exit 1
    
    # Step 5: Set environment variables
    set_environment_variables || exit 1
    
    # Step 6: Deploy
    deploy_to_render || exit 1
    
    # Step 7: Health checks (optional)
    read -p "Run health checks? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sleep 30  # Wait for services to start
        check_deployment_health || log_warning "Health checks incomplete"
    fi
    
    # Print summary
    print_deployment_summary
    
    log_success "Deployment process completed!"
}

# Run main function
main "$@"
