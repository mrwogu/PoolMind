# 🎱 PoolMind

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-red.svg)](https://fastapi.tiangolo.com/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://mrwogu.github.io/PoolMind/)

**Open-source AI pool assistant for Raspberry Pi with overhead camera computer vision and real-time game analysis.**

> 📹 **Overhead Camera Required**: Designed for ceiling-mounted camera installation above pool table center for bird's-eye view perspective.

![PoolMind Demo](https://user-images.githubusercontent.com/placeholder/demo.gif)

## ✨ Features

- 🎥 **Real-time Ball Tracking** - ArUco-calibrated computer vision with HSV color detection
- 🎯 **Automatic Calibration** - Perspective correction using corner markers (IDs 0,1,2,3)
- � **8-Ball Rules Engine** - Complete game state management with foul detection
- 📹 **Motion Replay System** - Automatic clip recording with MP4 export
- 🌐 **Web Dashboard** - Live MJPEG streaming and game statistics
- ⚡ **Auto-Deployment** - One-line installation with automatic GitHub updates
- 🔧 **Modular Architecture** - Extensible components for custom rules and detectors
- 🎮 **Advanced Physics Simulator** - Testing and development without hardware

## 📋 System Requirements

### 🎯 Camera Setup (Critical)
- **Position**: Mounted **directly above table center** (ceiling mount recommended)
- **Height**: 2-3 meters above surface for full table coverage
- **Angle**: Perfect **90° downward** (bird's-eye view essential)
- **Camera**: USB 1080p, wide-angle lens preferred

### 💻 Hardware
- **Raspberry Pi 4** (4GB+ RAM) or equivalent ARM64/x86_64 Linux system
- **ArUco Markers**: Print provided A4 PDF and mount at table corners
- **Optional**: HDMI display for full-screen live view

> ⚠️ **Important**: Side-mounted or angled cameras will not work. The system requires overhead perspective for ArUco homography and accurate ball tracking.

## 🚀 Quick Installation

### Option 1: Auto-Install (Recommended)
```bash
# One command installs everything and sets up auto-updates:
curl -fsSL https://raw.githubusercontent.com/mrwogu/PoolMind/main/install.sh | bash
```

### Option 2: Manual Setup
```bash
# Clone and install:
git clone https://github.com/mrwogu/PoolMind.git
cd PoolMind
./scripts/setup/setup-pi.sh

# Or for development:
./scripts/setup/setup.sh
```

## 🚀 Next Steps

1. 🖨️ **Print markers**: `~/PoolMind/markers/markers_A4.pdf`
2. 📍 **Place markers**: At table corners (0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left)
3. 🌐 **Access dashboard**: `http://your-pi-ip:8000`
4. 🎱 **Start playing pool!**

**The system will:**
- ✅ Auto-start on boot
- ✅ Auto-update every 30 minutes from GitHub
- ✅ Create backups before updates
- ✅ Restart service after updates
- ✅ Run web interface on port 8000

## 🛠️ Management Commands

```bash
# Check system status
./scripts/deployment/status.sh

# Force update now
./scripts/deployment/update.sh

# View live logs
sudo journalctl -u poolmind -f

# Restart service
sudo systemctl restart poolmind
```

## 🧪 Development & Testing

### Local Development Setup
```bash
git clone https://github.com/mrwogu/PoolMind.git
cd PoolMind
./scripts/setup/setup.sh    # Creates venv, installs deps, pre-commit hooks
source .venv/bin/activate
./scripts/setup/run.sh       # Starts application
```

### Testing Without Hardware
```bash
# Physics simulation demo
./scripts/demo/physics_simulator.py

# Enhanced PoolMind pipeline simulation
./scripts/demo/enhanced_simulation.py

# Simple virtual table
./scripts/demo/demo.py
```

### Remote Deployment
```bash
# Deploy from any machine to Pi
./scripts/deployment/deploy-remote.sh 192.168.1.100
```

## 🏗️ Architecture Overview

PoolMind uses a modular computer vision pipeline:

```
📷 Camera → 🎯 ArUco Detection → 📐 Homography → 🎱 Ball Detection → 📊 Tracking → 🎮 Game Engine → 🌐 Web Interface
```

**Key Components:**
- **ArUco Calibration** (`poolmind.calib`) - Perspective correction using corner markers
- **Ball Detection** (`poolmind.detect`) - HSV-based color classification with HoughCircles
- **Object Tracking** (`poolmind.track`) - Centroid-based tracking with ID persistence
- **Game Engine** (`poolmind.game`) - 8-ball rules with foul detection
- **Web Interface** (`poolmind.web`) - FastAPI dashboard with MJPEG streaming
- **Replay System** (`poolmind.services`) - Motion-triggered recording

## 📖 Documentation

**Complete documentation available at: [https://mrwogu.github.io/PoolMind/](https://mrwogu.github.io/PoolMind/)**

### Quick Links
- [📋 Configuration Guide](https://mrwogu.github.io/PoolMind/CONFIGURATION/) - Camera and detection settings
- [🎯 Calibration Setup](https://mrwogu.github.io/PoolMind/CALIBRATION/) - ArUco marker positioning
- [🌐 Web Interface](https://mrwogu.github.io/PoolMind/WEB/) - Dashboard and API reference
- [🏗️ Architecture](https://mrwogu.github.io/PoolMind/ARCHITECTURE/) - System design and components
- [🎱 ArUco Markers](https://mrwogu.github.io/PoolMind/MARKERS/) - Marker setup and troubleshooting

## 📁 Project Structure

```
PoolMind/
├── 🐍 src/poolmind/           # Main Python package
│   ├── calib/                 # ArUco calibration
│   ├── detect/                # Ball detection algorithms
│   ├── track/                 # Object tracking
│   ├── game/                  # 8-ball rules engine
│   ├── web/                   # FastAPI web interface
│   └── services/              # Replay and utilities
├── �️ scripts/                # Management and setup scripts
│   ├── setup/                 # Installation scripts
│   ├── demo/                  # Simulation and testing
│   ├── deployment/            # Auto-update system
│   └── tools/                 # Utilities and markers
├── ⚙️ config/                 # Configuration files
├── � docs/                   # GitHub Pages documentation
└── 🎯 markers/                # Generated ArUco markers
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-amazing-feature`
3. Follow [Conventional Commits](https://www.conventionalcommits.org/): `feat: add trajectory prediction`
4. Commit changes: `git commit -m "feat: add trajectory prediction"`
5. Push branch: `git push origin feature-amazing-feature`
6. Submit Pull Request

**Pre-commit hooks automatically:**
- ✅ Format code with Black
- ✅ Sort imports with isort
- ✅ Lint with flake8
- ✅ Validate commit messages with gitlint

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [OpenCV](https://opencv.org/) for computer vision
- [FastAPI](https://fastapi.tiangolo.com/) for web interface
- [ArUco markers](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html) for calibration
- Designed for [Raspberry Pi](https://www.raspberrypi.org/) deployment

---

**⭐ Star this repository if PoolMind helps improve your pool game!**


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
