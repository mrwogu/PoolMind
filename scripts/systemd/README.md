# ⚙️ Systemd Service Files

Systemd configuration files for running PoolMind as a production service on Linux systems (especially Raspberry Pi).

## 📋 Files Overview

| File | Purpose | Type | Schedule |
|------|---------|------|----------|
| [`poolmind.service`](poolmind.service) | **Main application service** | Service | Always running |
| [`poolmind-update.service`](poolmind-update.service) | **Update service** | Service | On-demand |
| [`poolmind-update.timer`](poolmind-update.timer) | **Update scheduler** | Timer | Daily at 3 AM |

## 🚀 Installation

### Automatic Installation

Services are automatically installed by the setup script:

```bash
# Production setup installs services
../setup/setup-pi.sh
```

### Manual Installation

If you need to install services manually:

```bash
# Copy service files
sudo cp *.service /etc/systemd/system/
sudo cp *.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable poolmind.service
sudo systemctl enable poolmind-update.timer

# Start services
sudo systemctl start poolmind.service
sudo systemctl start poolmind-update.timer
```

## 🔧 Service Configuration

### Main Service (`poolmind.service`)

**Purpose:** Runs PoolMind as a system service

**Key features:**
- Automatic startup on boot
- Restart on failure
- Proper user permissions
- Environment variable setup
- Logging to journal

**Service definition:**
```ini
[Unit]
Description=PoolMind - AI Pool Assistant
After=network.target
Wants=network.target

[Service]
Type=simple
User=poolmind
Group=poolmind
WorkingDirectory=/opt/poolmind
Environment=PYTHONPATH=/opt/poolmind/src
ExecStart=/opt/poolmind/.venv/bin/python -m poolmind.app --config config/config.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Update Service (`poolmind-update.service`)

**Purpose:** Handles automatic updates

**Features:**
- Safe update process
- Backup before update
- Service restart after update
- Error handling and rollback
- Update notification

**Update process:**
1. Stop main service
2. Backup current version
3. Pull latest code
4. Update dependencies
5. Restart main service
6. Validate update success

### Update Timer (`poolmind-update.timer`)

**Purpose:** Schedules automatic updates

**Default schedule:** Daily at 3:00 AM
**Configurable:** Edit timer for different schedule

```ini
[Unit]
Description=PoolMind Update Timer
Requires=poolmind-update.service

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## 🎛️ Service Management

### Basic Operations

```bash
# Start service
sudo systemctl start poolmind

# Stop service
sudo systemctl stop poolmind

# Restart service
sudo systemctl restart poolmind

# Check status
sudo systemctl status poolmind

# Enable auto-start
sudo systemctl enable poolmind

# Disable auto-start
sudo systemctl disable poolmind
```

### Update Management

```bash
# Check update timer status
sudo systemctl status poolmind-update.timer

# Manual update trigger
sudo systemctl start poolmind-update

# View update schedule
sudo systemctl list-timers poolmind-update*

# Disable automatic updates
sudo systemctl disable poolmind-update.timer
```

### Monitoring

```bash
# Real-time logs
sudo journalctl -u poolmind -f

# Recent logs
sudo journalctl -u poolmind --since "1 hour ago"

# Update logs
sudo journalctl -u poolmind-update --since "1 day ago"

# Boot logs
sudo journalctl -u poolmind --boot
```

## 📊 Service Status Examples

### Healthy Service
```
● poolmind.service - PoolMind - AI Pool Assistant
   Loaded: loaded (/etc/systemd/system/poolmind.service; enabled)
   Active: active (running) since Mon 2024-01-15 14:30:22 UTC; 2h 15min ago
     Docs: https://github.com/mrwogu/PoolMind
 Main PID: 1234 (python)
    Tasks: 8 (limit: 4915)
   Memory: 156.2M
   CGroup: /system.slice/poolmind.service
           └─1234 /opt/poolmind/.venv/bin/python -m poolmind.app

Jan 15 16:45:12 raspberrypi poolmind[1234]: INFO: Ball potted: ID=5 (orange)
Jan 15 16:45:18 raspberrypi poolmind[1234]: INFO: Game state: Player 1 turn
```

### Service with Issues
```
● poolmind.service - PoolMind - AI Pool Assistant
   Loaded: loaded (/etc/systemd/system/poolmind.service; enabled)
   Active: failed (Result: exit-code) since Mon 2024-01-15 16:47:33 UTC; 2min ago
  Process: 1234 ExecStart=/opt/poolmind/.venv/bin/python -m poolmind.app (code=exited, status=1)
 Main PID: 1234 (code=exited, status=1)

Jan 15 16:47:33 raspberrypi poolmind[1234]: ERROR: Camera not found
Jan 15 16:47:33 raspberrypi systemd[1]: poolmind.service: Main process exited, code=exited, status=1/FAILURE
```

## 🔧 Configuration Customization

### Custom Installation Path

If PoolMind is installed in a different location:

```bash
# Edit service file
sudo systemctl edit poolmind.service

# Add override:
[Service]
WorkingDirectory=/home/pi/PoolMind
Environment=PYTHONPATH=/home/pi/PoolMind/src
ExecStart=/home/pi/PoolMind/.venv/bin/python -m poolmind.app --config config/config.yaml
```

### Different User

To run as a different user:

```bash
# Create user if needed
sudo useradd --system --home /opt/poolmind poolmind

# Edit service
sudo systemctl edit poolmind.service

[Service]
User=myuser
Group=mygroup
```

### Custom Update Schedule

Change update timing:

```bash
# Edit timer
sudo systemctl edit poolmind-update.timer

[Timer]
OnCalendar=*-*-* 02:00:00    # 2 AM instead of 3 AM
# OnCalendar=Sun *-*-* 04:00:00  # Sundays only at 4 AM
```

### Environment Variables

Add custom environment variables:

```bash
sudo systemctl edit poolmind.service

[Service]
Environment=DEBUG=1
Environment=CAMERA_DEVICE=/dev/video1
Environment=WEB_PORT=8080
```

## 🔐 Security Configuration

### User Permissions

Service runs with minimal privileges:

```bash
# Service user should own application files
sudo chown -R poolmind:poolmind /opt/poolmind

# Set proper permissions
sudo chmod 755 /opt/poolmind
sudo chmod -R 644 /opt/poolmind/config/
sudo chmod +x /opt/poolmind/.venv/bin/python
```

### Camera Access

Grant camera access to service user:

```bash
# Add user to video group
sudo usermod -a -G video poolmind

# Set camera permissions
sudo chmod 666 /dev/video0
```

### Network Security

Limit network access if needed:

```bash
# Firewall rules (example)
sudo ufw allow from 192.168.1.0/24 to any port 8000
sudo ufw deny 8000
```

## 🐛 Troubleshooting

### Service Won't Start

**Check service status:**
```bash
sudo systemctl status poolmind
sudo journalctl -u poolmind --since "10 minutes ago"
```

**Common issues:**
- Missing dependencies: `pip install -r requirements.txt`
- Permission problems: Check file ownership
- Config file errors: Validate YAML syntax
- Camera access: Check device permissions

### Service Crashes

**Check crash logs:**
```bash
sudo journalctl -u poolmind --since "1 hour ago" --priority=err
```

**Debug process:**
```bash
# Run manually to see errors
sudo -u poolmind bash
cd /opt/poolmind
source .venv/bin/activate
export PYTHONPATH=/opt/poolmind/src
python -m poolmind.app --config config/config.yaml
```

### Update Failures

**Check update logs:**
```bash
sudo journalctl -u poolmind-update --since "1 day ago"
```

**Manual update:**
```bash
# Run update script manually
sudo -u poolmind /opt/poolmind/scripts/deployment/update.sh
```

### Performance Issues

**Monitor resource usage:**
```bash
# CPU and memory
systemd-cgtop

# Service-specific
systemctl status poolmind
sudo systemd-analyze plot > boot.svg  # Boot time analysis
```

## 📋 Maintenance Tasks

### Regular Checks

```bash
# Weekly service health check
sudo systemctl is-active poolmind
sudo journalctl -u poolmind --since "1 week ago" --priority=warning

# Monthly update review
sudo journalctl -u poolmind-update --since "1 month ago"
```

### Log Rotation

```bash
# Clean old logs (systemd handles rotation)
sudo journalctl --vacuum-time=30d
sudo journalctl --vacuum-size=100M
```

### Backup Service Configuration

```bash
# Backup service files
cp /etc/systemd/system/poolmind* ~/poolmind-services-backup/

# Backup with system configuration
sudo systemctl show poolmind > poolmind-config-backup.txt
```

---

💡 **Production Tip**: Always test service configuration in development before deploying to production systems.
