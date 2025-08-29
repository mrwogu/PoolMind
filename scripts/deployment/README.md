# 🚀 Deployment Scripts

Scripts for deploying, updating, and managing PoolMind installations in production environments.

## 📋 Scripts Overview

| Script | Purpose | Use Case | Environment |
|--------|---------|----------|-------------|
| [`auto-update.sh`](auto-update.sh) | **Automatic updates** | Systemd timer | Production |
| [`update.sh`](update.sh) | **Manual updates** | Maintenance | Any |
| [`deploy-remote.sh`](deploy-remote.sh) | **Remote deployment** | CI/CD, remote management | Development → Production |
| [`status.sh`](status.sh) | **System status** | Monitoring, troubleshooting | Production |
| [`validate-renovate.sh`](validate-renovate.sh) | **CI validation** | Dependency updates | CI/CD |

## 🚀 Usage

### Manual Update

Update existing PoolMind installation:

```bash
./update.sh
```

**What it does:**
- Stops running services
- Pulls latest code from git
- Updates Python dependencies
- Restarts services
- Validates update success

### Remote Deployment

Deploy to Raspberry Pi from development machine:

```bash
./deploy-remote.sh pi@192.168.1.100
```

**What it does:**
- Copies code to remote machine
- Runs remote update process
- Validates deployment
- Provides status feedback

**Requirements:**
- SSH access to target machine
- PoolMind already installed on target

### System Status Check

Monitor production system:

```bash
./status.sh
```

**Output includes:**
- Service status (systemd)
- Resource usage (CPU, memory)
- Recent logs
- Camera connection
- Network status

### Automatic Updates

Enable automatic updates (production):

```bash
# Setup done by setup-pi.sh, but manual enable:
sudo systemctl enable poolmind-update.timer
sudo systemctl start poolmind-update.timer
```

**Schedule:** Daily at 3 AM
**Safety:** Only updates if git repo is clean

## 🔧 Configuration

### Update Settings

Edit update behavior in scripts:

```bash
# In update.sh
UPDATE_BRANCH="main"           # Branch to update from
RESTART_SERVICES=true          # Auto-restart after update
BACKUP_CONFIG=true             # Backup config before update
```

### Remote Deployment

Configure SSH access:

```bash
# Setup SSH key authentication
ssh-copy-id pi@192.168.1.100

# Test connection
ssh pi@192.168.1.100 "systemctl --user status poolmind"
```

### Auto-Update Schedule

Modify timer schedule:

```bash
# Edit timer
sudo systemctl edit poolmind-update.timer

# Add override:
[Timer]
OnCalendar=*-*-* 03:00:00
```

## 📊 Monitoring & Logs

### Service Logs

```bash
# Real-time logs
sudo journalctl -u poolmind -f

# Recent logs
sudo journalctl -u poolmind --since "1 hour ago"

# Update logs
sudo journalctl -u poolmind-update --since "1 day ago"
```

### System Health

```bash
./status.sh  # Comprehensive status

# Or individual checks:
systemctl status poolmind
ps aux | grep poolmind
df -h  # Disk space
free -h  # Memory usage
```

### Performance Monitoring

```bash
# CPU usage
top -p $(pgrep -f poolmind)

# Network connections
ss -tulpn | grep poolmind

# GPU usage (Pi 4 with GPU acceleration)
vcgencmd measure_temp
vcgencmd get_mem gpu
```

## 🔄 Update Process Flow

### Manual Update (`update.sh`)

1. **Pre-update checks**
   - Verify git repository status
   - Check available disk space
   - Backup current configuration

2. **Update process**
   - Stop PoolMind service
   - Pull latest code
   - Update dependencies
   - Run database migrations (if any)

3. **Post-update validation**
   - Start services
   - Health check
   - Log update results

### Automatic Update (`auto-update.sh`)

1. **Safety checks**
   - Repository is clean (no local changes)
   - System has adequate resources
   - No critical errors in logs

2. **Update execution**
   - Same as manual update
   - Additional logging for unattended operation

3. **Notification**
   - Log results to systemd journal
   - Send notifications (if configured)

## 🐛 Troubleshooting

### Update Failures

**Git conflicts:**
```bash
# Check status
git status

# Reset to clean state (loses local changes!)
git reset --hard origin/main

# Then retry update
./update.sh
```

**Dependency issues:**
```bash
# Clear pip cache
pip cache purge

# Recreate virtual environment
rm -rf .venv
../setup/setup.sh
```

**Service won't start:**
```bash
# Check detailed error
sudo journalctl -u poolmind --no-pager

# Validate configuration
python -m poolmind.app --config config/config.yaml --validate

# Test manually
source .venv/bin/activate
export PYTHONPATH="$(pwd)/src"
python -m poolmind.app
```

### Remote Deployment Issues

**SSH connection fails:**
```bash
# Test connection
ssh -vvv pi@192.168.1.100

# Check SSH service on target
sudo systemctl status ssh
```

**Permission denied:**
```bash
# Check file permissions
ls -la ~/.ssh/
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### Resource Issues

**Disk space:**
```bash
# Clean old logs
sudo journalctl --vacuum-time=30d

# Clean pip cache
pip cache purge

# Remove old backups
find . -name "*.backup.*" -mtime +30 -delete
```

**Memory issues:**
```bash
# Check memory usage
free -h

# Restart services to free memory
sudo systemctl restart poolmind

# Check for memory leaks
valgrind python -m poolmind.app
```

## 🔒 Security Considerations

### SSH Security
- Use key-based authentication
- Disable password authentication
- Use non-standard SSH port
- Configure fail2ban

### Service Security
- Run as non-root user
- Limit network exposure
- Regular security updates
- Monitor access logs

### Backup Strategy
- Configuration files backed up before updates
- Regular system backups
- Test restore procedures

---

💡 **Best Practice**: Always test updates in development environment before deploying to production.
