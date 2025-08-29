#!/bin/bash

# Manual Update Script for PoolMind
# Quick way to manually trigger an update

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    error "This script must be run as the pi user"
fi

log "Triggering manual PoolMind update..."

# Run the auto-update script
if [ -f "/home/pi/PoolMind/scripts/auto-update.sh" ]; then
    /home/pi/PoolMind/scripts/auto-update.sh
else
    error "Auto-update script not found. Please run setup-pi.sh first."
fi

log "Manual update completed!"
