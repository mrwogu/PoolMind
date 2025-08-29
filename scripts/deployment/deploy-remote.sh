#!/bin/bash

# Remote Deployment Script for PoolMind
# This script deploys PoolMind to a remote Raspberry Pi via SSH

set -e

# Configuration
PI_USER="${PI_USER:-pi}"
PI_HOST="${PI_HOST}"
PI_PORT="${PI_PORT:-22}"
REPO_URL="https://github.com/mrwogu/PoolMind.git"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Usage
usage() {
    echo "Usage: $0 <pi-ip-address> [options]"
    echo ""
    echo "Options:"
    echo "  -u, --user USER     SSH username (default: pi)"
    echo "  -p, --port PORT     SSH port (default: 22)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 192.168.1.100"
    echo "  $0 192.168.1.100 -u pi -p 22"
    echo ""
    echo "Environment variables:"
    echo "  PI_USER             SSH username"
    echo "  PI_HOST             Raspberry Pi IP address"
    echo "  PI_PORT             SSH port"
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            exit 0
            ;;
        -u|--user)
            PI_USER="$2"
            shift 2
            ;;
        -p|--port)
            PI_PORT="$2"
            shift 2
            ;;
        -*)
            error "Unknown option: $1"
            ;;
        *)
            if [ -z "$PI_HOST" ]; then
                PI_HOST="$1"
            else
                error "Too many arguments"
            fi
            shift
            ;;
    esac
done

# Check if PI_HOST is provided
if [ -z "$PI_HOST" ]; then
    error "Raspberry Pi IP address is required"
fi

log "Starting remote deployment to $PI_USER@$PI_HOST:$PI_PORT"

# Test SSH connection
info "Testing SSH connection..."
if ! ssh -q -o ConnectTimeout=10 -p "$PI_PORT" "$PI_USER@$PI_HOST" exit; then
    error "Cannot connect to $PI_USER@$PI_HOST:$PI_PORT"
fi
log "SSH connection successful"

# Check if git is installed on Pi
info "Checking prerequisites on Raspberry Pi..."
ssh -p "$PI_PORT" "$PI_USER@$PI_HOST" "command -v git >/dev/null 2>&1" || {
    warning "Git not found on Raspberry Pi, installing..."
    ssh -p "$PI_PORT" "$PI_USER@$PI_HOST" "sudo apt update && sudo apt install -y git"
}

# Deploy PoolMind
log "Deploying PoolMind..."

ssh -p "$PI_PORT" "$PI_USER@$PI_HOST" << 'EOF'
set -e

# Download and run setup script
if [ ! -d "/home/pi/PoolMind" ]; then
    echo "Cloning PoolMind repository..."
    git clone https://github.com/mrwogu/PoolMind.git /home/pi/PoolMind
else
    echo "PoolMind already exists, updating..."
    cd /home/pi/PoolMind
    git fetch origin
    git reset --hard origin/main
fi

# Make setup script executable and run it
cd /home/pi/PoolMind
chmod +x scripts/setup/setup-pi.sh
./scripts/setup/setup-pi.sh
EOF

# Get Pi IP for web interface
PI_IP=$(ssh -p "$PI_PORT" "$PI_USER@$PI_HOST" "hostname -I | awk '{print \$1}'")

log "Deployment completed successfully!"
echo
info "PoolMind is now running on your Raspberry Pi"
info "Web interface: http://$PI_IP:8000"
echo
info "SSH commands to manage PoolMind:"
info "  ssh -p $PI_PORT $PI_USER@$PI_HOST"
info "  /home/pi/PoolMind/scripts/deployment/status.sh"
info "  /home/pi/PoolMind/scripts/update.sh"
echo
info "The system will automatically check for updates every 30 minutes"
