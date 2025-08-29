# 🎱 PoolMind - Quick Start

## 🚀 One-Line Installation for Raspberry Pi

```bash
cd ~ && curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
```

## What happens next?

✅ **Automatic setup** (5-10 minutes):
- Installs all system dependencies
- Downloads PoolMind from GitHub
- Sets up Python environment
- Generates ArUco markers
- Configures auto-updates every 30 minutes
- Starts web interface on port 8000

✅ **Auto-updates forever**:
- Checks GitHub every 30 minutes
- Updates automatically when new version available
- Backs up before each update
- Restarts service automatically
- Starts on boot

## Next Steps

1. **🖨️ Print markers**: `~/PoolMind/markers/markers_A4.pdf`
2. **📍 Place markers**: At table corners (0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left)
3. **🌐 Open browser**: `http://your-pi-ip:8000`
4. **🎱 Play pool!**

## Management

```bash
# Check status
./scripts/deployment/status.sh

# Manual update
./scripts/deployment/update.sh

# View logs
sudo journalctl -u poolmind -f

# Restart
sudo systemctl restart poolmind
```

## Features

- 🎥 Live video stream with ball tracking
- 🎯 Automatic calibration using ArUco markers
- 🎱 Ball detection with color classification
- 📊 Game tracking with 8-ball rules
- 🌐 Web dashboard with dark/light mode
- 🔄 Auto-updates from GitHub
- 🚀 Zero-maintenance deployment

## Hardware Needed

- **Raspberry Pi 4** (4GB+ recommended)
- **USB camera** (1080p+) mounted overhead
- **Pool table**
- **Printer** for ArUco markers

---

**That's it! PoolMind will now run 24/7 and update itself automatically.**

📖 **Full documentation:** [README.md](README.md)
