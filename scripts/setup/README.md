# 🔧 Setup Scripts

Scripts for installing and configuring PoolMind in different environments.

## 📋 Scripts Overview

| Script | Purpose | Environment | Prerequisites |
|--------|---------|-------------|---------------|
| [`setup.sh`](setup.sh) | **Development setup** | Local development | Python 3.9+, git |
| [`setup-pi.sh`](setup-pi.sh) | **Production setup** | Raspberry Pi | Raspberry Pi OS |
| [`run.sh`](run.sh) | **Start application** | Any | Completed setup |

## 🚀 Usage

### Development Environment Setup

For local development on macOS/Linux:

```bash
./setup.sh
```

**What it does:**
- Creates Python virtual environment
- Installs all dependencies from `requirements.txt`
- Generates ArUco markers
- Sets up pre-commit hooks
- Validates installation

**Requirements:**
- Python 3.9 or higher
- Git (for pre-commit hooks)
- OpenCV dependencies (auto-installed)

### Production Raspberry Pi Setup

For production deployment on Raspberry Pi:

```bash
./setup-pi.sh
```

**What it does:**
- Installs system dependencies (OpenCV, camera libraries)
- Creates virtual environment
- Installs Python packages
- Configures systemd services
- Sets up auto-updates
- Configures camera permissions

**Requirements:**
- Raspberry Pi OS (Bullseye or newer)
- Internet connection
- sudo privileges

### Running PoolMind

After successful setup:

```bash
./run.sh
```

**What it does:**
- Activates virtual environment
- Sets PYTHONPATH
- Runs PoolMind with config
- Provides helpful error messages

## 🔍 Setup Details

### Virtual Environment
All setups create `.venv` in project root:
```bash
source .venv/bin/activate  # Manual activation
```

### Dependencies
Core packages installed:
- `opencv-python` - Computer vision
- `numpy` - Numerical computing
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pyyaml` - Configuration parsing

### Configuration
Setup scripts ensure:
- Config file exists at `config/config.yaml`
- ArUco markers generated in `markers/`
- Proper file permissions
- Environment variables set

## 🐛 Troubleshooting

### Common Issues

**Python version too old:**
```bash
python3 --version  # Should be 3.9+
```

**OpenCV installation fails:**
```bash
# On macOS
brew install opencv

# On Raspberry Pi (auto-handled by setup-pi.sh)
sudo apt-get install python3-opencv
```

**Camera permission denied:**
```bash
# Add user to video group (Raspberry Pi)
sudo usermod -a -G video $USER
```

**Virtual environment issues:**
```bash
# Remove and recreate
rm -rf .venv
./setup.sh
```

### Validation

Test setup success:
```bash
# Check Python imports
source .venv/bin/activate
python -c "import cv2, numpy; print('✅ Core imports OK')"

# Test camera (if available)
../tools/camera_test.py --list-cameras

# Run demo mode
../demo/demo.py
```

## 🔄 Update Process

To update existing installation:
```bash
# Pull latest code
git pull

# Re-run setup (safe to repeat)
./setup.sh

# Or use update script
../deployment/update.sh
```

## 🏗️ Advanced Configuration

### Custom Python Path
```bash
export PYTHON_PATH="/usr/local/bin/python3.10"
./setup.sh
```

### Development Dependencies
```bash
# Install additional dev tools
pip install -r requirements-dev.txt
```

### Camera Configuration
Edit `config/config.yaml` after setup:
```yaml
camera:
  device_id: 0      # Change if multiple cameras
  resolution: [1920, 1080]
  fps: 30
```

---

💡 **Next Steps**: After setup, try running `../demo/demo.py` to test the system without camera hardware.
