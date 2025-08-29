#!/bin/bash

# PoolMind Auto-Update Script
# This script pulls the latest version from GitHub and restarts the service

set -e  # Exit on any error

# Configuration
REPO_DIR="/home/pi/PoolMind"
SERVICE_NAME="poolmind"
LOG_FILE="/home/pi/poolmind-update.log"
BACKUP_DIR="/home/pi/PoolMind-backups"
MAX_BACKUPS=5

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    error_exit "This script must be run as the pi user"
fi

log "Starting PoolMind auto-update process"

# Check if repository directory exists
if [ ! -d "$REPO_DIR" ]; then
    error_exit "Repository directory $REPO_DIR does not exist"
fi

cd "$REPO_DIR" || error_exit "Failed to change to repository directory"

# Check if this is a git repository
if [ ! -d ".git" ]; then
    error_exit "Directory $REPO_DIR is not a git repository"
fi

# Fetch the latest changes
log "Fetching latest changes from GitHub..."
git fetch origin || error_exit "Failed to fetch from origin"

# Check if there are any updates available
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    log "Already up to date (commit: ${LOCAL_COMMIT:0:8})"
    exit 0
fi

log "Update available: ${LOCAL_COMMIT:0:8} -> ${REMOTE_COMMIT:0:8}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create backup of current version
BACKUP_NAME="poolmind-backup-$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

log "Creating backup: $BACKUP_NAME"
cp -r "$REPO_DIR" "$BACKUP_PATH" || error_exit "Failed to create backup"

# Remove old backups (keep only the latest MAX_BACKUPS)
log "Cleaning up old backups..."
cd "$BACKUP_DIR"
ls -1t poolmind-backup-* 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -rf
cd "$REPO_DIR"

# Stop the service
log "Stopping PoolMind service..."
if systemctl is-active --quiet "$SERVICE_NAME"; then
    sudo systemctl stop "$SERVICE_NAME" || error_exit "Failed to stop service"
    log "Service stopped successfully"
else
    log "Service was not running"
fi

# Pull the latest changes
log "Pulling latest changes..."
git reset --hard origin/main || error_exit "Failed to reset to origin/main"
git clean -fd || error_exit "Failed to clean repository"

# Update Python dependencies if requirements changed
if git diff --name-only HEAD~1 HEAD | grep -q "requirements"; then
    log "Requirements files changed, updating dependencies..."
    source .venv/bin/activate || error_exit "Failed to activate virtual environment"

    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || error_exit "Failed to install requirements"
    fi

    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt || error_exit "Failed to install dev requirements"
    fi

    deactivate
fi

# Reload systemd in case service file changed
if git diff --name-only HEAD~1 HEAD | grep -q "scripts/poolmind.service"; then
    log "Service file changed, reloading systemd..."
    sudo systemctl daemon-reload || error_exit "Failed to reload systemd"
fi

# Start the service
log "Starting PoolMind service..."
sudo systemctl start "$SERVICE_NAME" || error_exit "Failed to start service"

# Wait a moment and check if service started successfully
sleep 5
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "Service started successfully"
    NEW_COMMIT=$(git rev-parse HEAD)
    log "Update completed successfully: ${NEW_COMMIT:0:8}"
else
    error_exit "Service failed to start after update"
fi

# Get service status for logging
SERVICE_STATUS=$(systemctl status "$SERVICE_NAME" --no-pager --lines=5)
log "Service status:"
echo "$SERVICE_STATUS" >> "$LOG_FILE"

log "Auto-update process completed successfully"
