# PoolMind Simulation Scripts

This directory contains scripts for testing and simulating the PoolMind application without requiring a physical pool table.

## 🎯 Available Simulation Options

### 1. **Virtual Table Simulator** (`virtual_table.py`)
Generates a synthetic pool table image with ArUco markers and simulated balls.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src:$(pwd)/scripts"
python scripts/virtual_table.py
```

**Features:**
- ✅ Realistic pool table appearance
- ✅ 4 ArUco markers in correct positions (0,1,2,3)
- ✅ 15 balls in triangle formation + cue ball
- ✅ Animated ball movements
- ✅ Interactive ball potting (SPACE)

**Controls:**
- `SPACE` - Pot random ball
- `R` - Reset balls to initial position
- `Q/ESC` - Exit

### 2. **Simple Computer Vision Demo** (`simple_demo.py`)
Complete PoolMind computer vision pipeline simulation with virtual table.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src:$(pwd)/scripts"
python scripts/simple_demo.py
```

**Tests:**
- ✅ ArUco marker detection
- ✅ Ball detection (HoughCircles)
- ✅ Ball color classification
- ✅ Results visualization
- ✅ Performance measurement (FPS)

**Controls:**
- `SPACE` - Pot random ball
- `R` - Reset simulation
- `Q/ESC` - Exit

### 3. **Camera Test Tool** (`camera_test.py`)
Test with real USB/built-in camera.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src"
python scripts/camera_test.py --camera 0
```

**Features:**
- ✅ Test different cameras (`--camera 0,1,2...`)
- ✅ List available cameras (`--list-cameras`)
- ✅ Live ArUco marker detection
- ✅ Ball detection on green background
- ✅ Table area mask
- ✅ Frame saving (`S`)

**Controls:**
- `A` - Toggle ArUco markers
- `B` - Toggle ball detection
- `T` - Toggle table mask overlay
- `S` - Save current frame
- `Q/ESC` - Exit

### 4. **Component Demo** (`demo.py`)
Original component test without graphics - game logic testing.

```bash
cd PoolMind
export PYTHONPATH="$(pwd)/src"
python scripts/demo.py
```

## 🛠️ Configuration

All scripts use the `config/config.yaml` file. You can adjust:

```yaml
camera:
  width: 1280
  height: 720
  fps: 30

detection:
  hsv_green_lower: [35, 30, 30]   # Green table color range
  hsv_green_upper: [85, 255, 255]
  ball_min_radius: 8              # Min ball radius
  ball_max_radius: 18             # Max ball radius
  hough_dp: 1.2                   # HoughCircles parameters
  hough_min_dist: 16
  hough_param1: 120
  hough_param2: 18

calibration:
  corner_ids: [0, 1, 2, 3]        # ArUco marker IDs
  table_w: 2000                   # Table dimensions (pixels)
  table_h: 1000
```

## 📋 Troubleshooting

### ArUco Markers not detected
```bash
# Check OpenCV version
python -c "import cv2; print(cv2.__version__)"

# Check ArUco availability
python -c "import cv2.aruco; print('ArUco available')"
```

### No ball detection
- Check lighting - needs uniform illumination
- Adjust HSV parameters for table green in config.yaml
- Adjust HoughCircles parameters

### Camera not working
```bash
# List available cameras
python scripts/camera_test.py --list-cameras

# Test specific camera
python scripts/camera_test.py --camera 1
```

### ArUco Markers - printing
```bash
# Generate markers for printing
cd PoolMind
export PYTHONPATH="$(pwd)/src"
python scripts/gen_markers.py --out markers --ids 0 1 2 3 --px 1200 --pdf
```

Print `markers/markers_A4.pdf` and place markers:
- `0` - top-left corner
- `1` - top-right corner
- `2` - bottom-right corner
- `3` - bottom-left corner

## 🎮 Use Cases

### Development without hardware
Use `simple_demo.py` for:
- Testing detection algorithms
- UI development
- Game logic debugging
- Feature demonstrations

### Camera calibration
Use `camera_test.py` for:
- Testing image quality
- Checking marker detection
- Adjusting HSV parameters
- Optimizing camera position

### System integration
Use `virtual_table.py` for:
- AI/model training
- Test data generation
- End-to-end pipeline testing
- Client presentations

## 📊 Performance Benchmark

| Script | FPS (typical) | CPU Usage | Description |
|--------|---------------|-----------|-------------|
| `virtual_table.py` | 30+ | Low | Image generation only |
| `simple_demo.py` | 20-30 | Medium | CV pipeline |
| `camera_test.py` | 15-25 | Medium-High | Camera + CV |

## 🔧 Extensions

You can easily extend the scripts with:
- Video recording of simulations
- Telemetry data export
- Testing different algorithms
- Web application integration
- Automated regression tests

## � Recent Updates

### ✅ Fixed ArUco Detection Issue (RESOLVED)

**Problem**: Virtual table was showing "detected 0/4" markers despite proper generation.

**Root Cause**: ArUco markers need sufficient contrast with background for detection.

**Solution Implemented**:
1. **Added white background padding** around each marker for contrast
2. **Removed noise interference** that was corrupting marker patterns
3. **Reordered rendering** to place markers after other elements

**Results**:
- ✅ Consistent **4/4 marker detection** in all scenarios
- ✅ **100% detection rate** in virtual table simulation
- ✅ **Stable homography** calculation for perspective correction

**Code Changes**:
```python
# Before: Markers placed directly on complex background
frame[y:y+size, x:x+size] = marker_img

# After: White background added for contrast
cv2.rectangle(frame, (x-5, y-5), (x+size+5, y+size+5), (255,255,255), -1)
frame[y:y+size, x:x+size] = marker_img
```

**Verification**:
```bash
# Test with debug script
PYTHONPATH=src python scripts/debug_markers.py
# Expected output: "✅ Found 4 markers: [2, 3, 1, 0]"
```

This fix ensures the virtual table simulation provides **reliable ArUco marker detection** for homography-based computer vision pipeline testing.

## �📖 More Information

- [Main Documentation](../docs/)
- [Configuration](../docs/CONFIGURATION.md)
- [Calibration](../docs/CALIBRATION.md)
- [Architecture](../docs/ARCHITECTURE.md)
