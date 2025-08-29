# 🎱 PoolMind

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-red.svg)](https://fastapi.tiangolo.com/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-C51A4A.svg)](https://www.raspberrypi.org/)

**Open-source AI pool assistant for Raspberry Pi with overhead camera computer vision and auto-deployment.**

> 📹 **Camera Setup**: Designed for overhead camera installation centrally mounted above the pool table for optimal bird's-eye view perspective.

<!-- ![PoolMind Demo](docs/images/demo.gif) -->

## ✨ Features

- 🎥 **Live HDMI Display** - Full-screen real-time visualization with game overlays
- 🎯 **ArUco Calibration** - Automatic camera perspective correction using corner markers
- 🎱 **Smart Ball Detection** - Advanced HSV-based color classification (cue, solid, stripe)
- 📊 **Real-time Tracking** - Centroid-based ball tracking with motion prediction
- 🎮 **8-Ball Rules Engine** - Automatic game state management and foul detection
- 📹 **Instant Replay** - Motion-triggered recording with MP4 export
- 🌐 **Web Dashboard** - FastAPI-powered interface with live MJPEG streaming
- 🔧 **Modular Design** - Extensible architecture for custom detectors and rules
- ⚡ **Production Ready** - Systemd service integration and graceful error handling

## 🎯 Hardware Requirements

### Camera Setup
- **Position**: Camera must be mounted **directly above the pool table center**
- **Height**: 2-3 meters above the table surface for optimal coverage
- **Angle**: Perfect **90° downward** angle (bird's-eye view)
- **Field of View**: Must capture the entire table surface plus marker placement area

### Recommended Hardware
- **Computer**: Raspberry Pi 4 (4GB+ RAM) or equivalent Linux SBC
- **Camera**: USB camera with 1080p resolution, wide-angle lens preferred
- **Mounting**: Ceiling mount or adjustable arm for stable positioning
- **Markers**: Print the included ArUco markers and place at table corners

> ⚠️ **Critical**: Overhead camera positioning is essential for accurate ball tracking and game analysis. Side-angle or tilted cameras will not work correctly.

## 🚀 Quick Start

### 🎯 Just Run It (Raspberry Pi)

**Single command to install and run everything:**

```bash
cd ~ && curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
```

**Then:**
1. 🖨️ Print `~/PoolMind/markers/markers_A4.pdf`
2. 📍 Place markers at table corners (0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left)
3. 🌐 Open `http://your-pi-ip:8000` in browser
4. 🎱 Start playing pool!

### 🛠️ Development Setup

**For local development and testing:**

```bash
cd ~ && git clone https://github.com/mrwogu/PoolMind.git && cd PoolMind
./scripts/setup/setup.sh
source .venv/bin/activate
./scripts/setup/run.sh
```

> **📖 See [scripts/README.md](scripts/README.md) for complete script documentation**

## 📋 Installation & Usage

### 🎯 Production Setup (Raspberry Pi)

**One command installs everything:**

```bash
cd ~ && curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
```

**What this does:**
- ✅ Installs all system dependencies (OpenCV, camera libraries)
- ✅ Sets up Python environment with virtual environment
- ✅ Clones repository and installs Python packages
- ✅ Generates ArUco markers automatically
- ✅ Configures systemd services for auto-start on boot
- ✅ Enables auto-updates every 30 minutes from GitHub
- ✅ Starts web interface immediately on port 8000

**After installation:**
1. 🖨️ Print `~/PoolMind/markers/markers_A4.pdf`
2. 📍 Place markers at table corners: **0 (top-left), 1 (top-right), 2 (bottom-right), 3 (bottom-left)**
3. 🌐 Open `http://<raspberry-pi-ip>:8000` in browser

### 🛠️ Development Setup

**For local development and testing:**

```bash
cd ~ && git clone https://github.com/mrwogu/PoolMind.git && cd PoolMind
./scripts/setup/setup.sh        # Set up development environment
source .venv/bin/activate        # Activate Python environment
./scripts/setup/run.sh           # Start application
```

**Development workflow:**
```bash
# Test without camera (useful for non-Pi development)
./scripts/demo/demo.py

# Run with camera
./scripts/setup/run.sh

# Check system status (Pi only)
./scripts/deployment/status.sh
```

### 📋 Scripts Reference

| Command | Purpose | Use Case |
|---------|---------|----------|
| `./scripts/setup/setup.sh` | Development environment | Local development setup |
| `./scripts/setup/setup-pi.sh` | Production Pi setup | Initial Pi installation |
| `./scripts/setup/run.sh` | Start application | Running PoolMind |
| `./scripts/demo/demo.py` | Demo without camera | Testing without hardware |
| `./scripts/deployment/status.sh` | System status | Health check and logs |
| `./scripts/deployment/update.sh` | Manual update | Force update Pi installation |

> **📖 Complete documentation:** [scripts/README.md](scripts/README.md)

## 🔄 Auto-Deployment System

PoolMind includes a complete auto-deployment solution for Raspberry Pi that automatically updates your installation with the latest code from GitHub.

### ✨ Auto-Deployment Features
- ✅ **One-line installation** - No manual setup required
- ✅ **Auto-updates** every 30 minutes from GitHub main branch
- ✅ **Backup system** with automatic rollback on failure
- ✅ **Systemd integration** with auto-start on boot
- ✅ **Dependency management** - automatically installs new requirements
- ✅ **Zero-downtime** updates with graceful service management
- ✅ **Camera auto-configuration** with proper permissions

### 📊 Management Commands

```bash
# Check system status and logs
./scripts/deployment/status.sh

# Force manual update
./scripts/deployment/update.sh

# Deploy to remote Pi from development machine
./scripts/deployment/deploy-remote.sh 192.168.1.100

# View live logs
sudo journalctl -u poolmind -f

# Restart service
sudo systemctl restart poolmind
```

### 🔧 How Auto-Updates Work

1. **Systemd timer** runs every 30 minutes
2. **Git fetch** checks for new commits on GitHub
3. **Backup creation** before making any changes
4. **Service management**: stop → update code → install deps → restart
5. **Automatic rollback** if new version fails to start

> **📖 Advanced deployment:** [scripts/README.md](scripts/README.md)

## 📐 Configuration

The system is highly configurable through `config/config.yaml`. Key settings:

### Camera Settings
```yaml
camera:
  device: 0              # Camera device index (/dev/video0)
  resolution: [1920, 1080]  # Capture resolution
  fps: 30                # Frames per second
```

### Detection Parameters
```yaml
detection:
  ball_radius_range: [8, 25]  # Min/max ball radius in pixels
  hough_circles:
    dp: 1.2              # Accumulator resolution ratio
    min_dist: 30         # Minimum distance between circles
    param1: 100          # Edge detection threshold
    param2: 30           # Center detection threshold
```

### Game Logic
```yaml
game:
  pocket_zones:
    radius: 40           # Pocket detection radius
  disappear_threshold: 5  # Frames before ball considered potted
```

> **📖 Complete reference:** [docs/CONFIGURATION.md](docs/CONFIGURATION.md)

## 🏗️ Architecture

The system follows a modular pipeline architecture:

```
📷 Camera → 🎯 ArUco → 🔄 Homography → 🎱 Detection → 📊 Tracking → 🎮 Game Engine → 🌐 Web UI
```

### Core Components

| Module | Purpose | Key Features |
|--------|---------|--------------|
| `capture/camera.py` | Video input | Threaded capture, hardware abstraction |
| `calib/markers.py` | Calibration | ArUco detection, homography with EMA smoothing |
| `detect/balls.py` | Ball detection | HoughCircles + HSV color classification |
| `track/tracker.py` | Object tracking | Centroid tracking with ID persistence |
| `table/geometry.py` | Table geometry | Perspective warping, pocket zones |
| `game/engine.py` | Game logic | 8-ball rules, pocket detection, scoring |
| `web/server.py` | Web interface | FastAPI, MJPEG streaming, real-time stats |
| `services/replay.py` | Recording | Motion-triggered MP4 generation |

## 📱 Web Dashboard

Access at `http://<raspberry-pi-ip>:8000`

**Features:**
- **🔴 Live Stream** - Real-time MJPEG video feed with overlays
- **📊 Game Statistics** - Ball counts, scores, game state
- **🎮 Controls** - Start/stop, calibration, settings
- **📹 Replay Browser** - View and download recorded clips
- **⚙️ Configuration** - Adjust parameters in real-time

**API Endpoints:**
- `/` - Web dashboard
- `/stream.mjpg` - MJPEG live stream
- `/state` - JSON game state
- `/events` - Recent game events
- `/markers/download` - Download ArUco markers PDF

## 🔧 Development

### Local Development Setup

```bash
cd ~ && git clone https://github.com/mrwogu/PoolMind.git && cd PoolMind
./scripts/setup/setup.sh        # Set up development environment
source .venv/bin/activate        # Activate Python environment
```

### Testing Without Hardware

```bash
# Demo mode (creates synthetic frames)
./scripts/demo/demo.py

# Web server only
PYTHONPATH=src python -m uvicorn poolmind.web.server:app --reload
```

### Contributing

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feat/amazing-feature`
3. **Commit** with conventional commits: `git commit -m 'feat: add amazing feature'`
4. **Push** to branch: `git push origin feat/amazing-feature`
5. **Open** a Pull Request

**Commit format:** This project uses [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add new feature
fix: resolve camera bug
docs: update installation guide
```

> **🛠️ Development guide:** [.github/copilot-instructions.md](.github/copilot-instructions.md)

## 🐛 Troubleshooting

### Camera Issues

```bash
# List available cameras
v4l2-ctl --list-devices

# Test camera
ffplay /dev/video0

# Fix permissions
sudo usermod -a -G video $USER
```

### ArUco Markers Not Detected

- **Lighting:** Ensure even lighting without glare
- **Print Quality:** Use high-quality printer, no scaling
- **Placement:** Markers flat, all 4 corners visible
- **Distance:** Camera should clearly see all markers

### Poor Ball Detection

- **Lighting:** Consistent room lighting
- **Focus:** Sharp camera focus
- **Parameters:** Tune HoughCircles settings in config
- **Colors:** Calibrate HSV ranges for your ball set

### Service Issues

```bash
# Check status
sudo systemctl status poolmind

# View logs
sudo journalctl -u poolmind -f

# Restart
sudo systemctl restart poolmind
```

## 📚 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System design and components
- **[Configuration](docs/CONFIGURATION.md)** - Complete parameter reference
- **[Calibration](docs/CALIBRATION.md)** - Camera and marker setup
- **[Web Interface](docs/WEB.md)** - Dashboard and API guide
- **[ArUco Markers](docs/MARKERS.md)** - Marker generation and placement
- **[Scripts](scripts/README.md)** - Complete script reference

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenCV** community for computer vision tools
- **ArUco** marker detection algorithms
- **FastAPI** for excellent web framework
- **Raspberry Pi Foundation** for affordable computing

---

**🎱 PoolMind - Open Source Pool Computer Vision Assistant**
