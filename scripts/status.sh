#!/bin/bash

# PoolMind Status Check Script
# Shows current status of PoolMind services and system

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

status_ok() {
    echo -e "${GREEN}✓ $1${NC}"
}

status_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

status_error() {
    echo -e "${RED}✗ $1${NC}"
}

header "PoolMind System Status"

# Check if services exist
if systemctl list-unit-files | grep -q "poolmind.service"; then
    status_ok "PoolMind service is installed"

    # Check service status
    if systemctl is-active --quiet poolmind; then
        status_ok "PoolMind service is running"
    else
        status_error "PoolMind service is not running"
    fi

    if systemctl is-enabled --quiet poolmind; then
        status_ok "PoolMind service is enabled (auto-start)"
    else
        status_warning "PoolMind service is not enabled"
    fi
else
    status_error "PoolMind service is not installed"
fi

# Check auto-update timer
if systemctl list-unit-files | grep -q "poolmind-update.timer"; then
    status_ok "Auto-update timer is installed"

    if systemctl is-active --quiet poolmind-update.timer; then
        status_ok "Auto-update timer is running"
    else
        status_error "Auto-update timer is not running"
    fi
else
    status_error "Auto-update timer is not installed"
fi

echo

# Show git status
header "Repository Status"
if [ -d "/home/pi/PoolMind/.git" ]; then
    cd /home/pi/PoolMind
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    CURRENT_BRANCH=$(git branch --show-current)

    git fetch origin >/dev/null 2>&1
    REMOTE_COMMIT=$(git rev-parse --short origin/main)

    echo "Current branch: $CURRENT_BRANCH"
    echo "Local commit:   $CURRENT_COMMIT"
    echo "Remote commit:  $REMOTE_COMMIT"

    if [ "$CURRENT_COMMIT" = "$REMOTE_COMMIT" ]; then
        status_ok "Repository is up to date"
    else
        status_warning "Updates available"
    fi
else
    status_error "Repository not found"
fi

echo

# Show recent service logs
header "Recent Service Logs (last 5 lines)"
if systemctl list-unit-files | grep -q "poolmind.service"; then
    sudo journalctl -u poolmind --no-pager --lines=5
else
    echo "Service not installed"
fi

echo

# Show update logs if they exist
header "Recent Update Logs"
if [ -f "/home/pi/poolmind-update.log" ]; then
    echo "Last 5 update log entries:"
    tail -n 5 /home/pi/poolmind-update.log
else
    echo "No update logs found"
fi

echo

# System info
header "System Information"
echo "Hostname: $(hostname)"
echo "IP Address: $(hostname -I | awk '{print $1}')"
echo "Uptime: $(uptime -p)"
echo "CPU Temperature: $(vcgencmd measure_temp 2>/dev/null || echo 'N/A')"
echo "Memory Usage: $(free -h | grep Mem | awk '{print $3 "/" $2}')"

echo

# Web interface status
header "Web Interface"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000 | grep -q "200"; then
    status_ok "Web interface is accessible at http://$(hostname -I | awk '{print $1}'):8000"
else
    status_warning "Web interface not responding"
fi

echo

header "Quick Commands"
echo "• View live logs: sudo journalctl -u poolmind -f"
echo "• Restart service: sudo systemctl restart poolmind"
echo "• Manual update: /home/pi/PoolMind/scripts/update.sh"
echo "• Stop service: sudo systemctl stop poolmind"
echo "• Start service: sudo systemctl start poolmind"
