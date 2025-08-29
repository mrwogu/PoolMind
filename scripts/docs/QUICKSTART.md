# 🚀 PoolMind Auto-Deployment - Quick Reference

## One-Line Installation

```bash
# Install everything with one command:
curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash

# Alternative - deploy remotely from any machine:
git clone https://github.com/mrwogu/PoolMind.git && cd PoolMind && ./scripts/deployment/deploy-remote.sh 192.168.1.100

# Or directly on Pi (if you cloned repo):
git clone https://github.com/mrwogu/PoolMind.git && cd PoolMind && ./scripts/setup/setup-pi.sh
```

## What Happens After Setup

✅ **PoolMind automatically:**
- Starts on boot
- Checks for GitHub updates every 30 minutes
- Downloads and installs updates automatically
- Restarts service after updates
- Creates backups before each update
- Runs web interface on port 8000

## Management Commands

```bash
# Check everything is working
./scripts/deployment/status.sh

# Force update now
./scripts/deployment/update.sh

# Watch live logs
sudo journalctl -u poolmind -f

# Restart service
sudo systemctl restart poolmind
```

## Web Interface
Access at: **http://your-pi-ip:8000**

## That's It!
Your Pi now auto-updates PoolMind from GitHub and runs it 24/7.

---
*See [scripts/README.md](README.md) for detailed documentation*
