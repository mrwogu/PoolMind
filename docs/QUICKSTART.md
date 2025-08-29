# 🎱 PoolMind - Quick Start

> 📖 **Main Documentation**: For complete installation guide and project overview, see the [main README.md](https://github.com/mrwogu/PoolMind/blob/main/README.md)

## 🚀 One-Line Installation

**Raspberry Pi Auto-Installation:**
```bash
curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
```

**Development Setup:**
```bash
git clone https://github.com/mrwogu/PoolMind.git
cd PoolMind
./scripts/setup/setup.sh
```

## 📋 Hardware Setup

### Required Hardware
- **Raspberry Pi 4** (4GB+ RAM recommended)
- **USB Camera** (1080p+) with overhead mounting
- **Pool Table** with space for markers
- **Printer** for ArUco markers

### Camera Positioning (Critical)
- **Mount overhead** - directly above table center
- **Height**: 2-3 meters above surface
- **Angle**: Perfect 90° downward (bird's-eye view)
- **Coverage**: Full table must be visible

> ⚠️ **Important**: Side-mounted cameras will not work. Overhead positioning is essential.

## 🎯 Setup Steps

1. **Install** - Run installation command above
2. **Print** - Print `~/PoolMind/markers/markers_A4.pdf`
3. **Mount** - Place markers at table corners:
   - `0` - Top-left corner
   - `1` - Top-right corner
   - `2` - Bottom-right corner
   - `3` - Bottom-left corner
4. **Access** - Open `http://your-pi-ip:8000` in browser
5. **Play** - Start playing pool!

## 🛠️ Management

```bash
# Check status
./scripts/deployment/status.sh

# Force update
./scripts/deployment/update.sh

# View logs
sudo journalctl -u poolmind -f

# Restart service
sudo systemctl restart poolmind
```

## 🧪 Testing & Development

```bash
# Test without hardware
./scripts/demo/enhanced_simulation.py

# Physics simulation
./scripts/demo/physics_simulator.py

# Camera test
./scripts/tools/camera_test.py --list-cameras
```

## ⚡ Auto-Update Features

After installation, PoolMind automatically:
- ✅ Starts on boot
- ✅ Checks GitHub for updates every 30 minutes
- ✅ Downloads and installs updates
- ✅ Creates backups before updates
- ✅ Restarts service after updates
- ✅ Provides web interface on port 8000

## 📖 More Information

- **[Configuration Guide](CONFIGURATION.md)** - Camera and detection settings
- **[Calibration Setup](CALIBRATION.md)** - ArUco marker positioning
- **[Web Interface](WEB.md)** - Dashboard and API reference
- **[Architecture](ARCHITECTURE.md)** - System design and components
- **[Simulation Scripts](SIMULATION.md)** - Testing without hardware

---

**⭐ For complete documentation, see the [main README.md](https://github.com/mrwogu/PoolMind/blob/main/README.md)**
