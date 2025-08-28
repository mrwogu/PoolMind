# 📁 PoolMind Scripts Reference

This directory contains all scripts for running, developing, and deploying PoolMind. Choose the right script for your use case.

## 🚀 Quick Reference

### Just Want to Run It?

```bash
# 🎯 Production on Raspberry Pi (auto-installs everything)
cd ~ && curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash

# 🛠️ Development setup (if you cloned the repo)
cd ~/PoolMind && ./scripts/setup.sh && ./scripts/run.sh

# 🎮 Demo mode (no camera required)
cd ~/PoolMind && source .venv/bin/activate && python scripts/demo.py
```

### Need to Manage the System?

```bash
# Check system status
./scripts/status.sh

# Manual update
./scripts/update.sh

# Deploy to remote Pi
./scripts/deploy-remote.sh 192.168.1.100
```

## � Complete Scripts Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| [`setup.sh`](#setupsh) | **Development environment** | Setting up for local development |
| [`setup-pi.sh`](#setup-pish) | **Production Raspberry Pi setup** | Initial Pi installation with services |
| [`run.sh`](#runsh) | **Start application** | Running PoolMind locally |
| [`demo.py`](#demopy) | **Demo without camera** | Testing without hardware |
| [`auto-update.sh`](#auto-updatesh) | **Automatic updates** | Called by systemd timer |
| [`update.sh`](#updatesh) | **Manual update** | Update existing installation |
| [`status.sh`](#statussh) | **System status** | Check health and logs |
| [`deploy-remote.sh`](#deploy-remotesh) | **Remote deployment** | Deploy to Pi from another machine |
| [`gen_markers.py`](#gen_markerspy) | **Generate ArUco markers** | Create printable calibration markers |
| [`validate-renovate.sh`](#validate-renovatesh) | **CI validation** | Check dependency updates |

## 🛠️ Development Scripts

### `setup.sh`

**Purpose:** Set up complete development environment on macOS/Linux

**Usage:**
```bash
cd ~/PoolMind
./scripts/setup.sh
```

**What it does:**
- ✅ Creates Python virtual environment
- ✅ Installs all dependencies
- ✅ Installs pre-commit hooks with conventional commits validation
- ✅ Generates ArUco markers
- ✅ Configures git commit template
- ✅ Tests installation

**Requirements:** Python 3.8+, Node.js (for gitlint)

### `run.sh`

**Purpose:** Start PoolMind application

**Usage:**
```bash
cd ~/PoolMind
./scripts/run.sh
```

**What it does:**
- Activates virtual environment
- Sets PYTHONPATH
- Runs main application with default config
- Starts web server on port 8000

**Environment variables:**
```bash
# Custom config
CONFIG_FILE=config/custom.yaml ./scripts/run.sh

# Debug mode
DEBUG=1 ./scripts/run.sh
```

### `demo.py`

**Purpose:** Test PoolMind without camera hardware

**Usage:**
```bash
cd ~/PoolMind
source .venv/bin/activate
python scripts/demo.py
```

**Features:**
- Creates synthetic video frames
- Tests game engine logic
- Validates component imports
- Useful for development on non-Pi systems

## 🚀 Production Scripts

### `setup-pi.sh`

**Purpose:** Complete Raspberry Pi production setup

**Usage:**
```bash
# Direct execution on Pi
cd ~/PoolMind && ./scripts/setup-pi.sh

# Or via install.sh
curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
```

**What it does:**
- ✅ Installs system dependencies (OpenCV, camera libs)
- ✅ Creates Python environment
- ✅ Configures camera permissions
- ✅ Sets up systemd services (poolmind.service)
- ✅ Enables auto-updates (poolmind-update.timer)
- ✅ Configures auto-start on boot
- ✅ Creates backup system

**Services created:**
- `poolmind.service` - Main application
- `poolmind-update.service` - Update service
- `poolmind-update.timer` - Runs updates every 30 minutes

### `auto-update.sh`

**Purpose:** Automatic updates called by systemd timer

**Usage:** *(Called automatically, don't run manually)*

**What it does:**
- Checks for new commits on GitHub
- Creates backup before update
- Pulls latest changes
- Updates dependencies if requirements changed
- Restarts services if needed
- Logs all operations

### `update.sh`

**Purpose:** Manual update trigger

**Usage:**
```bash
cd ~/PoolMind
./scripts/update.sh
```

**Use cases:**
- Force immediate update
- After making configuration changes
- Troubleshooting auto-update issues

## 🔧 Management Scripts

### `status.sh`

**Purpose:** System health and status check

**Usage:**
```bash
cd ~/PoolMind
./scripts/status.sh
```

**Shows:**
- Service status (running/stopped/failed)
- Recent log entries
- Update status
- Camera availability
- Port availability (8000)
- Python environment status

### `deploy-remote.sh`

**Purpose:** Deploy to remote Raspberry Pi from development machine

**Usage:**
```bash
./scripts/deploy-remote.sh <pi-ip-address> [username]
```

**Examples:**
```bash
# Deploy to Pi with default pi user
./scripts/deploy-remote.sh 192.168.1.100

# Deploy with custom username
./scripts/deploy-remote.sh 192.168.1.100 myuser
```

**What it does:**
- Copies project files via rsync
- Runs setup-pi.sh remotely
- Configures services
- Starts application

**Requirements:** SSH access to target Pi

## 🎯 Utility Scripts

### `gen_markers.py`

**Purpose:** Generate printable ArUco calibration markers

**Usage:**
```bash
cd ~/PoolMind
source .venv/bin/activate
python scripts/gen_markers.py --out markers --ids 0 1 2 3 --px 1200 --pdf
```

**Options:**
- `--out`: Output directory
- `--ids`: Marker IDs to generate
- `--px`: Image size in pixels
- `--pdf`: Generate combined PDF

**Output:**
- Individual PNG files (aruco_0.png, aruco_1.png, etc.)
- Combined A4 PDF (markers_A4.pdf)

### `validate-renovate.sh`

**Purpose:** CI validation for dependency updates

**Usage:** *(Used in CI pipeline)*

**What it does:**
- Validates renovate configuration
- Checks for dependency conflicts
- Ensures compatibility

## ⚙️ Systemd Services

### `poolmind.service`

Main application service:

```ini
[Unit]
Description=PoolMind AI Pool Assistant
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/PoolMind
ExecStart=/home/pi/PoolMind/scripts/run.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### `poolmind-update.timer`

Automatic update timer:

```ini
[Unit]
Description=PoolMind Auto Update Timer

[Timer]
OnBootSec=5min
OnUnitActiveSec=30min
Persistent=true

[Install]
WantedBy=timers.target
```

## 🐛 Troubleshooting

### Common Issues

**Camera not detected:**
```bash
# Check camera permissions
ls -l /dev/video*
groups $USER  # Should include 'video' group

# Test camera
v4l2-ctl --list-devices
```

**Service won't start:**
```bash
# Check service status
sudo systemctl status poolmind

# View detailed logs
sudo journalctl -u poolmind -f

# Check Python environment
cd ~/PoolMind && source .venv/bin/activate && python -c "import poolmind"
```

**Web interface not accessible:**
```bash
# Check if port is bound
sudo netstat -tlnp | grep :8000

# Check firewall
sudo ufw status

# Test locally
curl http://localhost:8000
```

**Update failures:**
```bash
# Check git status
cd ~/PoolMind && git status

# Reset to clean state
git reset --hard origin/main

# Manual update
./scripts/update.sh
```

## 📝 Development Workflow

### Local Development

1. **Initial setup:**
   ```bash
   cd ~ && git clone https://github.com/mrwogu/PoolMind.git && cd PoolMind
   ./scripts/setup.sh
   ```

2. **Daily development:**
   ```bash
   cd ~/PoolMind
   source .venv/bin/activate
   # Make changes...
   python scripts/demo.py  # Test without camera
   ./scripts/run.sh        # Test with camera
   ```

3. **Commit with conventional commits:**
   ```bash
   git add .
   git commit  # Uses template from .gitmessage
   ```

### Production Deployment

1. **Initial Pi setup:**
   ```bash
   cd ~ && curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
   ```

2. **Monitor system:**
   ```bash
   ./scripts/status.sh
   sudo journalctl -u poolmind -f
   ```

3. **Updates happen automatically** every 30 minutes, or manually with `./scripts/update.sh`
- **Update**: Pulls latest code and restarts service if changes detected
- **Rollback**: Backups available in `/home/pi/PoolMind-backups/`

### Service Management
- **Auto-start**: Service starts automatically on boot
- **Auto-restart**: Service restarts if it crashes
- **Logging**: All logs available via `journalctl`

## 🛠️ Configuration

### Update Frequency
Edit the timer in `/etc/systemd/system/poolmind-update.timer`:
```ini
[Timer]
OnCalendar=*:0/30  # Every 30 minutes
# OnCalendar=hourly  # Every hour
# OnCalendar=daily   # Daily at midnight
```

### Service Settings
Edit `/etc/systemd/system/poolmind.service` for service configuration.

## 📋 Common Commands

### Service Management
```bash
# Check service status
sudo systemctl status poolmind

# Start/stop/restart service
sudo systemctl start poolmind
sudo systemctl stop poolmind
sudo systemctl restart poolmind

# Enable/disable auto-start
sudo systemctl enable poolmind
sudo systemctl disable poolmind
```

### Update Management
```bash
# Check auto-update timer
sudo systemctl status poolmind-update.timer

# Start/stop auto-updates
sudo systemctl start poolmind-update.timer
sudo systemctl stop poolmind-update.timer

# Manual update
/home/pi/PoolMind/scripts/update.sh
```

### Logs and Debugging
```bash
# View live service logs
sudo journalctl -u poolmind -f

# View update logs
tail -f /home/pi/poolmind-update.log

# Check last update
sudo journalctl -u poolmind-update --lines=20

# System status
/home/pi/PoolMind/scripts/status.sh
```

## 🔍 Troubleshooting

### Service Won't Start
1. Check logs: `sudo journalctl -u poolmind -n 50`
2. Check camera permissions: `ls -l /dev/video*`
3. Test manually: `cd /home/pi/PoolMind && source .venv/bin/activate && python -m poolmind.app --config config/config.yaml`

### Updates Not Working
1. Check timer: `sudo systemctl status poolmind-update.timer`
2. Check update logs: `tail /home/pi/poolmind-update.log`
3. Test manual update: `/home/pi/PoolMind/scripts/update.sh`

### Web Interface Not Accessible
1. Check if service is running: `sudo systemctl status poolmind`
2. Check port: `netstat -tlnp | grep 8000`
3. Check firewall: `sudo ufw status`

### Camera Issues
1. Enable camera: `sudo raspi-config` → Interface Options → Camera
2. Check camera device: `ls /dev/video*`
3. Test camera: `raspistill -o test.jpg`

## 🔐 Security Considerations

- Service runs as `pi` user (not root)
- Limited file system access via systemd security settings
- Auto-updates only pull from trusted GitHub repository
- Backups created before each update

## 📊 Monitoring

### Web Interface
- Access at: `http://<pi-ip-address>:8000`
- Real-time video stream and game metrics
- Dark/light mode support

### System Status
- Use `./scripts/status.sh` for quick overview
- Service logs via `journalctl`
- Update history in `/home/pi/poolmind-update.log`

## 🔄 Rollback

If an update causes issues:

```bash
# Stop service
sudo systemctl stop poolmind

# List available backups
ls -la /home/pi/PoolMind-backups/

# Restore from backup (example)
cd /home/pi
rm -rf PoolMind
cp -r PoolMind-backups/poolmind-backup-20250829-120000 PoolMind

# Start service
sudo systemctl start poolmind
```

## 📱 Remote Management

You can manage PoolMind remotely via SSH:

```bash
# SSH into Raspberry Pi
ssh pi@<pi-ip-address>

# Check status
/home/pi/PoolMind/scripts/status.sh

# Manual update
/home/pi/PoolMind/scripts/update.sh

# View logs
sudo journalctl -u poolmind -f
```

## 🎯 Next Steps

After setup:
1. Configure camera settings in `config/config.yaml`
2. Adjust HSV color ranges for your lighting conditions
3. Print ArUco markers from `markers/` directory
4. Access web interface to test the system
5. Set up port forwarding for remote access (optional)

## 📞 Support

- Check logs first: `sudo journalctl -u poolmind`
- Run status check: `./scripts/status.sh`
- View recent updates: `tail /home/pi/poolmind-update.log`
- Manual testing: `PYTHONPATH=src python scripts/demo.py`
