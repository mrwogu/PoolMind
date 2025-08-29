#!/bin/bash

# PoolMind Development Setup Script
# Sets up development environment with all necessary dependencies

set -e

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

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running from project root
if [ ! -f "pyproject.toml" ] || [ ! -d "src/poolmind" ]; then
    error "Please run this script from the PoolMind project root directory"
    exit 1
fi

log "Starting PoolMind development environment setup..."

# Check Python version
python_version=$(python3 --version 2>&1 | grep -o "[0-9]\+\.[0-9]\+")
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    error "Python 3.8+ required, found Python $python_version"
    exit 1
fi
log "Python version check passed: $python_version"

# Create virtual environment
if [ ! -d ".venv" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv .venv
else
    info "Virtual environment already exists"
fi

# Activate virtual environment
log "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
log "Installing Python dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install package in development mode
log "Installing PoolMind in development mode..."
pip install -e .

# Install pre-commit hooks
log "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg

# Generate ArUco markers
log "Generating ArUco markers..."
export PYTHONPATH="$(pwd)/src"
python scripts/gen_markers.py --out markers --ids 0 1 2 3 --px 1200 --pdf

# Configure git commit template
log "Configuring git commit message template..."
git config commit.template .gitmessage

# Test installation
log "Testing installation..."
export PYTHONPATH="$(pwd)/src"
python -c "
import poolmind
from poolmind.detect.balls import BallDetector
from poolmind.track.tracker import CentroidTracker
from poolmind.calib.markers import MarkerHomography
print('✅ All imports successful')
"

log "Setup completed successfully!"
info "To activate the environment: source .venv/bin/activate"
info "To run demo: PYTHONPATH=src python scripts/demo.py"
info "To start web server: PYTHONPATH=src python -m uvicorn poolmind.web.server:app --host 0.0.0.0 --port 8000"
info "Commit messages will now be validated using conventional commits format via gitlint"
