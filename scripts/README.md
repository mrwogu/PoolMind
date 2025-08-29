# 📁 PoolMind Scripts Collection

**Reorganized and documented scripts** for PoolMind - AI pool assistant. Each category has its own directory with specialized tools and comprehensive documentation.

## 🚀 Quick Start

### 🎯 Interactive Navigation
```bash
# Use the interactive script navigator
./index.sh

# Or with quick commands:
./index.sh q  # Quick setup
./index.sh r  # Run PoolMind
./index.sh d  # Demo mode
./index.sh s  # System status
```

### 🎮 First Time Setup
```bash
# Development environment
./setup/setup.sh

# Demo mode (no camera required)
./demo/demo.py

# Production on Raspberry Pi
./setup/setup-pi.sh
```

## 📂 Organized Directory Structure

| Directory | Purpose | Key Scripts | Documentation |
|-----------|---------|-------------|---------------|
| [`setup/`](setup/) | **Installation & Configuration** | `setup.sh`, `setup-pi.sh`, `run.sh` | [📖 Setup Guide](setup/README.md) |
| [`deployment/`](deployment/) | **Deployment & Management** | `update.sh`, `deploy-remote.sh`, `status.sh` | [📖 Deployment Guide](deployment/README.md) |
| [`demo/`](demo/) | **Demos & Simulations** | `demo.py`, `virtual_table.py`, `full_simulation.py` | [📖 Demo Guide](demo/README.md) |
| [`testing/`](testing/) | **Testing & Debugging** | `debug_aruco.py`, `test_aruco.py`, `debug_markers.py` | [📖 Testing Guide](testing/README.md) |
| [`tools/`](tools/) | **Utilities & Generators** | `gen_markers.py`, `camera_test.py`, `inspect_frame.py` | [📖 Tools Guide](tools/README.md) |
| [`systemd/`](systemd/) | **System Services** | Service files, timers | [📖 Systemd Guide](systemd/README.md) |
| [`docs/`](docs/) | **Documentation** | README, guides, references | [📖 Documentation Index](docs/README.md) |

## 🎯 Common Workflows

### Development Workflow
```bash
# 1. Initial setup
./setup/setup.sh

# 2. Test without camera
./demo/demo.py

# 3. Test with camera
./tools/camera_test.py

# 4. Debug issues
./testing/debug_aruco.py

# 5. Run application
./setup/run.sh
```

### Production Deployment
```bash
# 1. Setup Raspberry Pi
./setup/setup-pi.sh

# 2. Deploy remotely (from dev machine)
./deployment/deploy-remote.sh pi@192.168.1.100

# 3. Check status
./deployment/status.sh

# 4. Apply updates
./deployment/update.sh
```

### Troubleshooting Workflow
```bash
# 1. Check system status
./deployment/status.sh

# 2. Test camera connection
./tools/camera_test.py --list-cameras

# 3. Debug ArUco detection
./testing/debug_aruco.py

# 4. Analyze problem frames
./tools/inspect_frame.py debug_frame.jpg

# 5. Re-generate markers if needed
./tools/gen_markers.py
```

## 🔧 Interactive Navigation

The `index.sh` script provides an **interactive menu system** for easy navigation:

```bash
./index.sh
```

**Features:**
- ✅ **Categorized menus** - Browse scripts by purpose
- ✅ **Quick actions** - Common tasks with single keypress
- ✅ **Built-in help** - Context-sensitive documentation
- ✅ **Environment setup** - Automatic PYTHONPATH and venv activation
- ✅ **Error handling** - Helpful error messages and recovery

**Quick Commands:**
- `./index.sh q` - Quick development setup
- `./index.sh r` - Run PoolMind application
- `./index.sh d` - Start demo mode
- `./index.sh s` - Check system status
- `./index.sh h` - Show help

## 📚 Documentation Standards

Each directory contains:

- **📖 README.md** - Comprehensive guide for that category
- **🔧 Usage examples** - Copy-paste ready commands
- **🐛 Troubleshooting** - Common issues and solutions
- **⚙️ Configuration** - Parameter tuning guides
- **🎯 Best practices** - Recommended workflows

### Documentation Quality
- ✅ **Example-driven** - Every concept includes working examples
- ✅ **Progressive complexity** - Simple to advanced usage
- ✅ **Cross-referenced** - Links between related concepts
- ✅ **Troubleshooting focused** - Common issues prominently featured
- ✅ **Copy-paste ready** - Commands work directly

## 🔍 Script Categories Explained

### 🔧 Setup & Installation
Essential scripts for getting PoolMind running:
- **Environment setup** - Python, dependencies, configuration
- **Hardware configuration** - Camera, permissions, calibration
- **Validation** - Test installation success

### 🚀 Deployment & Management
Production deployment and maintenance:
- **Remote deployment** - Deploy to Raspberry Pi from dev machine
- **Updates** - Automatic and manual update procedures
- **Monitoring** - System health and performance checks

### 🎮 Demos & Simulations
Test without physical hardware:
- **Full pipeline demos** - Complete computer vision stack
- **Virtual environments** - Synthetic pool table generation
- **Educational tools** - Learn computer vision concepts

### 🧪 Testing & Debugging
Validate and troubleshoot the system:
- **ArUco testing** - Marker detection validation
- **Algorithm debugging** - Step-by-step pipeline analysis
- **Performance profiling** - Optimization and benchmarking

### 🛠️ Tools & Utilities
Helper tools for development and maintenance:
- **Marker generation** - Create printable ArUco markers
- **Camera testing** - Hardware validation and tuning
- **Frame analysis** - Debug specific captured frames

### ⚙️ System Services
Production service management:
- **Systemd services** - Run as system daemon
- **Automatic updates** - Scheduled maintenance
- **Service monitoring** - Health checks and logging

## 💡 Best Practices

### Script Organization
- **Single responsibility** - Each script has one clear purpose
- **Consistent interface** - Similar usage patterns across scripts
- **Error handling** - Graceful failures with helpful messages
- **Documentation** - Every script includes usage help

### Development Workflow
- **Start with demos** - Test concepts without hardware
- **Incremental testing** - Validate each component separately
- **Configuration driven** - Use config files for parameters
- **Version control** - Track changes and configurations

### Production Deployment
- **Automated setup** - Use setup scripts, not manual commands
- **Service management** - Run as systemd services
- **Monitoring** - Regular health checks and log monitoring
- **Update procedures** - Safe, tested update processes

## 📊 Migration from Old Structure

The scripts have been reorganized for better maintainability:

**Old → New Mapping:**
- Root scripts → Categorized subdirectories
- Single README → Category-specific documentation
- Mixed purposes → Clear separation of concerns
- Manual navigation → Interactive menu system

**Benefits:**
- ✅ **Easier discovery** - Find relevant scripts faster
- ✅ **Better documentation** - Category-specific guides
- ✅ **Reduced complexity** - Clear separation of concerns
- ✅ **Improved maintenance** - Easier to update and extend

---

💡 **Getting Started**: Use `./index.sh` for interactive navigation, or jump directly to category READMEs for detailed documentation.
