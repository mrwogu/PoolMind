#!/bin/bash

# PoolMind Raspberry Pi Setup Script
# This script sets up PoolMind for auto-deployment on Raspberry Pi

set -e

# Configuration
REPO_URL="https://github.com/mrwogu/PoolMind.git"
INSTALL_DIR="/home/pi/PoolMind"
SERVICE_NAME="poolmind"
UPDATE_SERVICE_NAME="poolmind-update"
UPDATE_TIMER_NAME="poolmind-update.timer"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    error "This script must be run as the pi user"
fi

log "Starting PoolMind Raspberry Pi setup"

# Update system packages
log "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
log "Installing required system packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    libopencv-dev \
    python3-opencv \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test \
    libhdf5-dev \
    libhdf5-serial-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtgui4 \
    libqt4-test

# Enable camera if not already enabled
log "Checking camera configuration..."
if ! grep -q "start_x=1" /boot/config.txt; then
    warning "Camera not enabled in /boot/config.txt"
    info "You may need to run 'sudo raspi-config' and enable the camera"
fi

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    log "Repository already exists, updating..."
    cd "$INSTALL_DIR"
    git fetch origin
    git reset --hard origin/main
else
    log "Cloning PoolMind repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create virtual environment
log "Setting up Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
source .venv/bin/activate

log "Installing Python dependencies..."
pip install --upgrade pip
pip install wheel

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
fi

deactivate

# Make scripts executable
log "Setting up scripts..."
chmod +x scripts/deployment/auto-update.sh
chmod +x scripts/setup/setup-pi.sh

# Install systemd services
log "Installing systemd services..."

# Copy service files to systemd directory
sudo cp scripts/poolmind.service /etc/systemd/system/
sudo cp scripts/poolmind-update.service /etc/systemd/system/
sudo cp scripts/poolmind-update.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start main service
log "Enabling PoolMind service..."
sudo systemctl enable "$SERVICE_NAME"

# Enable auto-update timer
log "Enabling auto-update timer..."
sudo systemctl enable "$UPDATE_TIMER_NAME"
sudo systemctl start "$UPDATE_TIMER_NAME"

# Create log directory
mkdir -p /home/pi/logs

# Create config directory and copy default config if it doesn't exist
if [ ! -f "/home/pi/PoolMind/config/config.yaml" ]; then
    log "Creating default configuration..."
    mkdir -p config

    cat > config/config.yaml << 'EOF'
# PoolMind Configuration for Raspberry Pi

camera:
  device: 0  # Default camera device
  resolution: [640, 480]  # Lower resolution for Pi performance
  fps: 15  # Reduced FPS for stability

calibration:
  marker_size: 100
  ema_alpha: 0.3

detection:
  ball_min_radius: 8
  ball_max_radius: 25
  hough_dp: 1.2
  hough_min_dist: 30
  hough_param1: 50
  hough_param2: 30

  # HSV ranges for ball detection (adjust for your lighting)
  hsv_green_lower: [40, 40, 40]   # Table cloth
  hsv_green_upper: [80, 255, 255]

tracking:
  max_disappeared: 8
  max_distance: 40

game:
  disappear_for_pot: 6
  pocket_radius: 30
  enable_8ball_rules: true

table:
  table_w: 800   # Warped table width
  table_h: 400   # Warped table height
  margin: 30     # Pocket margin

web:
  enabled: true
  host: "0.0.0.0"
  port: 8000
  quality: 75  # JPEG quality for streaming
EOF
fi

# Test the service
log "Testing PoolMind service..."
if sudo systemctl start "$SERVICE_NAME"; then
    sleep 5
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log "Service started successfully!"
    else
        warning "Service failed to start properly"
        info "Check logs with: sudo journalctl -u $SERVICE_NAME -f"
    fi
else
    warning "Failed to start service"
fi

# Show status
log "Setup completed! Here's the status:"
echo
info "Main service status:"
sudo systemctl status "$SERVICE_NAME" --no-pager --lines=3

info "Auto-update timer status:"
sudo systemctl status "$UPDATE_TIMER_NAME" --no-pager --lines=3

echo
log "Setup completed successfully!"
info "PoolMind will now:"
info "  • Start automatically on boot"
info "  • Check for updates every 30 minutes"
info "  • Restart automatically after updates"
info "  • Run web interface on http://$(hostname -I | awk '{print $1}'):8000"
echo
info "Useful commands:"
info "  • Check service status: sudo systemctl status $SERVICE_NAME"
info "  • View logs: sudo journalctl -u $SERVICE_NAME -f"
info "  • Manual update: /home/pi/PoolMind/scripts/deployment/auto-update.sh"
info "  • Stop service: sudo systemctl stop $SERVICE_NAME"
info "  • Start service: sudo systemctl start $SERVICE_NAME"
echo
warning "Note: You may need to adjust camera settings and HSV ranges in config/config.yaml"
warning "Check the web interface at http://$(hostname -I | awk '{print $1}'):8000"
