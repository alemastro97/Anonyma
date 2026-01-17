#!/bin/bash

###############################################################################
# Anonyma - One-Command Setup Script
# Complete local deployment with Docker
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        echo "Please install Docker from https://www.docker.com/get-started"
        exit 1
    fi

    # Check for docker-compose (v1) or docker compose (v2)
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
        print_success "Docker and Docker Compose (v1) are installed"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
        print_success "Docker and Docker Compose (v2) are installed"
    else
        print_error "Docker Compose is not installed"
        echo "Please install Docker Compose"
        exit 1
    fi
}

# Generate secure random string
generate_secret() {
    openssl rand -hex 32
}

# Setup environment file
setup_env() {
    print_header "Environment Configuration"

    if [ -f .env ]; then
        print_warning ".env file already exists"
        read -p "Do you want to overwrite it? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Using existing .env file"
            return
        fi
    fi

    print_info "Creating .env file..."

    # Generate secrets
    JWT_SECRET=$(generate_secret)
    POSTGRES_PASSWORD=$(generate_secret | cut -c1-16)

    # Create .env file
    cat > .env << EOF
# ==================================
# Anonyma Configuration
# ==================================

# PostgreSQL
POSTGRES_DB=anonyma
POSTGRES_USER=anonyma
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
DATABASE_URL=postgresql://anonyma:${POSTGRES_PASSWORD}@postgres:5432/anonyma

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT Authentication
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API Configuration
ANONYMA_APP_NAME=Anonyma API
ANONYMA_DEBUG=false
ANONYMA_AUTH_ENABLED=true
ANONYMA_REDIS_ENABLED=true
ANONYMA_RATE_LIMIT_ENABLED=true

# Demo & Premium Limits
DEMO_MODE_ENABLED=true
DEMO_DAILY_LIMIT=50
DEMO_MONTHLY_LIMIT=500
PREMIUM_DAILY_LIMIT=1000
PREMIUM_MONTHLY_LIMIT=10000

# Frontend
REACT_APP_API_URL=http://localhost
FRONTEND_URL=http://localhost

# Default Admin (CHANGE THESE!)
DEFAULT_ADMIN_EMAIL=admin@anonyma.local
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=admin123

# Stripe (Optional - leave empty if not using)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID_PREMIUM=

# Email (Optional - leave empty if not using)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=
SMTP_FROM_NAME=Anonyma

# Ports
API_PORT=8000
NGINX_PORT=80
EOF

    print_success ".env file created"
    print_warning "IMPORTANT: Change DEFAULT_ADMIN_PASSWORD in .env before production!"
    echo ""
}

# Start services
start_services() {
    print_header "Starting Services"

    print_info "Building and starting Docker containers..."
    $DOCKER_COMPOSE -f docker-compose.full.yml up -d --build

    print_success "Services started successfully"
}

# Wait for services
wait_for_services() {
    print_header "Waiting for Services"

    print_info "Waiting for PostgreSQL..."
    sleep 5

    print_info "Waiting for API..."
    max_attempts=30
    attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "API is ready"
            break
        fi

        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    echo ""

    if [ $attempt -eq $max_attempts ]; then
        print_error "API failed to start. Check logs with:"
        echo "  docker-compose -f docker-compose.full.yml logs api"
        exit 1
    fi
}

# Show status
show_status() {
    print_header "Deployment Complete!"

    echo ""
    print_success "Anonyma is running!"
    echo ""
    echo "📍 Access URLs:"
    echo "   • Frontend:  http://localhost"
    echo "   • API:       http://localhost:8000"
    echo "   • API Docs:  http://localhost:8000/docs"
    echo ""
    echo "🔐 Admin Login:"
    echo "   • Username:  admin"
    echo "   • Password:  admin123 (change this!)"
    echo ""
    echo "🎯 Demo Mode:"
    echo "   • Click 'Try Demo Mode' on login page"
    echo "   • Limit: 50 requests/day"
    echo ""
    echo "📊 View logs:"
    echo "   $DOCKER_COMPOSE -f docker-compose.full.yml logs -f"
    echo ""
    echo "⏹️  Stop services:"
    echo "   $DOCKER_COMPOSE -f docker-compose.full.yml down"
    echo ""
    print_warning "Remember to change admin password in production!"
    echo ""
}

# Main execution
main() {
    clear
    print_header "Anonyma Setup"

    print_info "This script will set up Anonyma with Docker"
    echo ""

    # Check prerequisites
    check_docker

    # Setup environment
    setup_env

    # Start services
    start_services

    # Wait for services
    wait_for_services

    # Show status
    show_status
}

# Run main function
main
