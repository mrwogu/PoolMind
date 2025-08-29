#!/bin/bash

# PoolMind One-Line Installer for Raspberry Pi
# Usage: curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash

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
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
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

banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
    ____             ____  ____           __
   / __ \____  ____ / /  |/  (_)___  ____/ /
  / /_/ / __ \/ __ / / /|_/ / / __ \/ __  /
 / ____/ /_/ / /_/ / / /  / / / / / / /_/ /
/_/    \____/\____/_/_/  /_/_/_/ /_/\__,_/

🎱 AI Pool Assistant for Raspberry Pi
Auto-Deployment Installer
EOF
    echo -e "${NC}"
}

# Check if running as pi user
check_user() {
    if [ "$USER" != "pi" ]; then
        error "This script must be run as the pi user. Please switch to pi user: sudo su - pi"
    fi
}

# Check if running on Raspberry Pi
check_platform() {
    if [ ! -f /proc/device-tree/model ]; then
        warning "Not running on Raspberry Pi. This installer is optimized for Raspberry Pi."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Update system packages
update_system() {
    log "Updating system packages..."
    sudo apt update
    sudo apt upgrade -y
}

# Install required system packages
install_dependencies() {
    log "Installing system dependencies..."
    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        git \
        curl \
        wget \
        build-essential \
        cmake \
        pkg-config \
        libjpeg-dev \
        libtiff5-dev \
        libpng-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libfontconfig1-dev \
        libcairo2-dev \
        libgdk-pixbuf2.0-dev \
        libpango1.0-dev \
        libgtk2.0-dev \
        libgtk-3-dev \
        libatlas-base-dev \
        gfortran \
        libhdf5-dev \
        libhdf5-serial-dev \
        libhdf5-103 \
        libqt5gui5 \
        libqt5webkit5 \
        libqt5test5 \
        python3-pyqt5 \
        python3-opencv \
        libopencv-dev \
        v4l-utils \
        ffmpeg
}

# Enable camera if not already enabled
setup_camera() {
    log "Checking camera configuration..."

    # Check if camera is enabled in config.txt
    if ! grep -q "start_x=1" /boot/config.txt && ! grep -q "start_x=1" /boot/firmware/config.txt 2>/dev/null; then
        warning "Camera interface not enabled"
        info "Enabling camera interface..."

        # Try different locations for config.txt
        CONFIG_FILE=""
        if [ -f "/boot/firmware/config.txt" ]; then
            CONFIG_FILE="/boot/firmware/config.txt"
        elif [ -f "/boot/config.txt" ]; then
            CONFIG_FILE="/boot/config.txt"
        else
            warning "Could not find config.txt. Please enable camera manually with 'sudo raspi-config'"
            return
        fi

        # Enable camera
        echo "start_x=1" | sudo tee -a "$CONFIG_FILE"
        echo "gpu_mem=128" | sudo tee -a "$CONFIG_FILE"

        warning "Camera enabled. System will need to reboot after installation."
    else
        log "Camera interface is enabled"
    fi

    # Add user to video group
    sudo usermod -a -G video pi
}

# Clone repository
clone_repository() {
    log "Cloning PoolMind repository..."

    if [ -d "$INSTALL_DIR" ]; then
        warning "Directory $INSTALL_DIR already exists"
        read -p "Remove existing installation and reinstall? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            error "Installation cancelled"
        fi
    fi

    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
}

# Setup Python environment
setup_python() {
    log "Setting up Python virtual environment..."

    cd "$INSTALL_DIR"

    # Create virtual environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip wheel setuptools

    # Install requirements
    if [ -f "requirements.txt" ]; then
        log "Installing Python dependencies..."
        pip install -r requirements.txt
    fi

    if [ -f "requirements-dev.txt" ]; then
        log "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi

    deactivate
}

# Generate ArUco markers
generate_markers() {
    log "Generating ArUco markers..."

    cd "$INSTALL_DIR"
    source .venv/bin/activate

    # Create markers directory if it doesn't exist
    mkdir -p markers

    # Generate markers
    PYTHONPATH=src python scripts/tools/gen_markers.py --out markers --ids 0 1 2 3 --px 1200 --pdf

    deactivate

    log "ArUco markers generated in markers/ directory"
}

# Setup configuration
setup_config() {
    log "Setting up configuration..."

    cd "$INSTALL_DIR"
    mkdir -p config

    if [ ! -f "config/config.yaml" ]; then
        log "Creating default configuration..."

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
}

# Setup systemd services
setup_services() {
    log "Setting up systemd services..."

    cd "$INSTALL_DIR"

    # Make scripts executable
    chmod +x scripts/*/*.sh scripts/*.sh

    # Copy service files
    sudo cp scripts/systemd/poolmind.service /etc/systemd/system/
    sudo cp scripts/systemd/poolmind-update.service /etc/systemd/system/
    sudo cp scripts/systemd/poolmind-update.timer /etc/systemd/system/

    # Reload systemd
    sudo systemctl daemon-reload

    # Enable services
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl enable "$UPDATE_TIMER_NAME"

    log "Systemd services configured"
}

# Start services
start_services() {
    log "Starting PoolMind services..."

    # Start auto-update timer
    sudo systemctl start "$UPDATE_TIMER_NAME"

    # Start main service
    if sudo systemctl start "$SERVICE_NAME"; then
        sleep 5
        if systemctl is-active --quiet "$SERVICE_NAME"; then
            log "PoolMind service started successfully!"
        else
            warning "Service may have issues starting. Check logs with: sudo journalctl -u $SERVICE_NAME"
        fi
    else
        warning "Failed to start service. Check logs with: sudo journalctl -u $SERVICE_NAME"
    fi
}

# Show completion message
show_completion() {
    echo
    echo -e "${GREEN}🎉 PoolMind installation completed successfully!${NC}"
    echo

    # Get Pi IP address
    PI_IP=$(hostname -I | awk '{print $1}')

    info "🌐 Web interface: http://$PI_IP:8000"
    info "📁 Installation directory: $INSTALL_DIR"
    info "📄 Configuration file: $INSTALL_DIR/config/config.yaml"
    info "🖨️  Print markers: $INSTALL_DIR/markers/markers_A4.pdf"
    echo

    info "📊 Management commands:"
    echo "  • Check status:    $INSTALL_DIR/scripts/deployment/status.sh"
    echo "  • Manual update:   $INSTALL_DIR/scripts/deployment/update.sh"
    echo "  • View logs:       sudo journalctl -u poolmind -f"
    echo "  • Restart service: sudo systemctl restart poolmind"
    echo

    info "🔄 Auto-update features:"
    echo "  • Checks GitHub every 30 minutes for updates"
    echo "  • Automatically restarts service after updates"
    echo "  • Creates backups before each update"
    echo "  • Starts automatically on boot"
    echo

    # Check if reboot is needed
    if ! grep -q "start_x=1" /boot/config.txt && ! grep -q "start_x=1" /boot/firmware/config.txt 2>/dev/null; then
        warning "🔄 REBOOT REQUIRED for camera to work properly"
        echo
        read -p "Reboot now? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "Rebooting system..."
            sudo reboot
        else
            warning "Please reboot manually: sudo reboot"
        fi
    fi

    info "🎱 PoolMind is ready to use!"
    info "📖 Full documentation: https://github.com/mrwogu/PoolMind"
}

# Main installation function
main() {
    banner

    log "Starting PoolMind installation on Raspberry Pi"

    check_user
    check_platform
    update_system
    install_dependencies
    setup_camera
    clone_repository
    setup_python
    generate_markers
    setup_config
    setup_services
    start_services
    show_completion
}

# Run main function
main "$@"
