# 🔧 Tools & Utilities

Essential tools for PoolMind development, calibration, and maintenance.

## 📋 Tools Overview

| Tool | Purpose | Use Case | Hardware Required |
|------|---------|----------|-------------------|
| [`gen_markers.py`](gen_markers.py) | **Generate ArUco markers** | Initial setup, recalibration | None |
| [`camera_test.py`](camera_test.py) | **Camera testing & validation** | Hardware debugging | Camera |
| [`inspect_frame.py`](inspect_frame.py) | **Frame analysis** | Debug specific images | None |

## 🚀 Usage

### Generate ArUco Markers

Create printable ArUco markers for table calibration:

```bash
# Setup environment
source ../.venv/bin/activate
export PYTHONPATH="$(pwd)/../../src"

# Generate all markers
./gen_markers.py
```

**Output:**
- Individual PNG files: `aruco_0.png`, `aruco_1.png`, etc.
- Combined PDF: `markers_A4.pdf` (ready to print)
- High-resolution markers for accurate detection

**Customization:**
```bash
# Custom size (default: 200px)
./gen_markers.py --size 300

# Different dictionary
./gen_markers.py --dict DICT_6X6_250

# Output directory
./gen_markers.py --output ./custom_markers/
```

### Test Camera Setup

Validate camera hardware and detection pipeline:

```bash
# List available cameras
./camera_test.py --list-cameras

# Test specific camera
./camera_test.py --camera 0

# Full detection test
./camera_test.py --test-detection
```

**Test features:**
- Camera connection validation
- Resolution and FPS testing
- ArUco marker detection
- Ball detection validation
- Real-time performance metrics
- Frame capture and analysis

### Analyze Specific Frames

Debug issues with specific captured frames:

```bash
# Analyze debug frame
./inspect_frame.py debug_frame.jpg

# Detailed analysis with overlays
./inspect_frame.py --detailed debug_frame.jpg

# Batch analysis
./inspect_frame.py --batch ./debug_frames/
```

**Analysis includes:**
- Image quality metrics
- ArUco marker detection
- Ball detection results
- HSV color analysis
- Homography validation
- Performance profiling

## 🔧 Detailed Tool Usage

### ArUco Marker Generation (`gen_markers.py`)

**Purpose:** Create high-quality ArUco markers for table calibration.

**Key features:**
```python
# Marker specifications
MARKER_IDS = [0, 1, 2, 3]           # Corner markers
MARKER_SIZE = 200                   # Pixels (high resolution)
ARUCO_DICT = cv2.aruco.DICT_4X4_50  # Dictionary type
```

**Output formats:**
- **PNG files:** Individual markers for flexible placement
- **PDF layout:** A4 page with all markers positioned
- **Print guidelines:** Exact measurements for physical placement

**Usage scenarios:**
- Initial table setup
- Marker replacement
- Calibration accuracy improvement
- Different table sizes

**Advanced options:**
```bash
# High DPI for large tables
./gen_markers.py --size 400 --dpi 300

# Specific marker subset
./gen_markers.py --ids 0,1,2,3

# Custom border size
./gen_markers.py --border 50
```

### Camera Testing (`camera_test.py`)

**Purpose:** Comprehensive camera validation and debugging.

**Testing modes:**

1. **Basic connectivity:**
```bash
./camera_test.py --list-cameras
```
*Lists all available camera devices*

2. **Resolution testing:**
```bash
./camera_test.py --test-resolutions
```
*Tests supported resolutions and frame rates*

3. **Detection validation:**
```bash
./camera_test.py --test-detection
```
*Full computer vision pipeline test*

4. **Performance benchmarking:**
```bash
./camera_test.py --benchmark
```
*Measures FPS and latency*

**Interactive mode:**
```bash
./camera_test.py --interactive
```
*Real-time testing with live adjustments*

**Output information:**
```
📹 Camera Test Results:
Device: /dev/video0
Resolution: 1920x1080 @ 30 FPS
Markers detected: 4/4 (100%)
Balls detected: 12 ± 2
Avg processing time: 16.2ms
Quality score: 94/100 ✅
```

### Frame Inspection (`inspect_frame.py`)

**Purpose:** Detailed analysis of captured frames for debugging.

**Analysis types:**

1. **Basic inspection:**
```bash
./inspect_frame.py frame.jpg
```
*Quick overview of frame content*

2. **Computer vision analysis:**
```bash
./inspect_frame.py --cv-analysis frame.jpg
```
*ArUco detection, ball detection, HSV analysis*

3. **Quality assessment:**
```bash
./inspect_frame.py --quality-check frame.jpg
```
*Image quality metrics, noise analysis*

4. **Comparison mode:**
```bash
./inspect_frame.py --compare frame1.jpg frame2.jpg
```
*Side-by-side comparison*

**Detailed output:**
```
🔍 Frame Analysis: debug_frame.jpg
Dimensions: 1920x1080 (2.07 MP)
Bit depth: 8-bit RGB
Quality score: 87/100

📍 ArUco Markers:
✅ Marker 0: (123, 456) confidence: 0.98
✅ Marker 1: (789, 123) confidence: 0.95
⚠️  Marker 2: (456, 789) confidence: 0.82
❌ Marker 3: Not detected

🎱 Ball Detection:
Total detected: 11/16
Colors identified: 8 solid, 3 striped
Avg confidence: 0.91

📊 Quality Metrics:
Brightness: 142 (good)
Contrast: 0.67 (adequate)
Sharpness: 0.84 (good)
Noise level: 0.12 (low)
```

## 🎯 Common Workflows

### New Installation Setup

1. **Generate markers:**
```bash
./gen_markers.py
```

2. **Print and place markers** on table corners

3. **Test camera setup:**
```bash
./camera_test.py --test-detection
```

4. **Validate detection:**
```bash
./camera_test.py --benchmark
```

### Troubleshooting Poor Detection

1. **Capture problem frame:**
```bash
./camera_test.py --capture-frame debug_frame.jpg
```

2. **Analyze the frame:**
```bash
./inspect_frame.py --detailed debug_frame.jpg
```

3. **Check marker quality:**
```bash
# Re-generate if needed
./gen_markers.py --size 300 --high-quality
```

4. **Re-test:**
```bash
./camera_test.py --test-detection
```

### Performance Optimization

1. **Benchmark current performance:**
```bash
./camera_test.py --benchmark --save-results baseline.json
```

2. **Test different resolutions:**
```bash
./camera_test.py --resolution-sweep
```

3. **Optimize parameters** in `config.yaml`

4. **Compare performance:**
```bash
./camera_test.py --benchmark --compare baseline.json
```

## 🔧 Configuration

### Marker Generation Settings

```python
# In gen_markers.py
CONFIG = {
    "marker_size": 200,              # Pixels
    "border_bits": 1,                # Border width
    "dict_type": "DICT_4X4_50",     # ArUco dictionary
    "output_format": "both",         # "png", "pdf", or "both"
    "dpi": 300,                     # Print resolution
    "page_size": "A4"               # PDF page size
}
```

### Camera Test Parameters

```python
# In camera_test.py
TEST_CONFIG = {
    "resolutions": [(640,480), (1280,720), (1920,1080)],
    "fps_targets": [15, 30, 60],
    "test_duration": 30,             # Seconds
    "detection_threshold": 0.8,      # Confidence
    "performance_samples": 100       # Frames for benchmark
}
```

### Frame Inspection Settings

```python
# In inspect_frame.py
ANALYSIS_CONFIG = {
    "show_overlays": True,           # Visual annotations
    "save_analyzed": True,           # Save annotated frame
    "detail_level": "full",          # "basic", "normal", "full"
    "export_data": False,           # Export analysis JSON
    "comparison_mode": "auto"        # Side-by-side layout
}
```

## 🐛 Troubleshooting

### Camera Issues

**Camera not detected:**
```bash
# Check device permissions
ls -la /dev/video*
sudo usermod -a -G video $USER

# Test with v4l2 (Linux)
v4l2-ctl --list-devices
v4l2-ctl --device=/dev/video0 --all
```

**Poor image quality:**
```bash
# Test different resolutions
./camera_test.py --resolution-sweep

# Check camera settings
./camera_test.py --show-properties

# Manual camera adjustment
v4l2-ctl --device=/dev/video0 --set-ctrl=brightness=150
```

### Marker Generation Issues

**Low print quality:**
```bash
# Increase resolution
./gen_markers.py --size 400 --dpi 600

# Check printer settings (high quality, no compression)
```

**Detection problems:**
```bash
# Test marker quality
./inspect_frame.py marker_test.jpg

# Regenerate with different parameters
./gen_markers.py --dict DICT_6X6_250 --border 2
```

### Performance Issues

**Slow processing:**
```bash
# Profile performance
./camera_test.py --profile

# Test lower resolution
./camera_test.py --resolution 640x480

# Check system resources
top -p $(pgrep -f camera_test)
```

## 📊 Output Examples

### Successful Marker Detection
```
🎯 Marker Generation Complete!
Generated files:
├── markers/aruco_0.png (200x200, 98% quality)
├── markers/aruco_1.png (200x200, 98% quality)
├── markers/aruco_2.png (200x200, 98% quality)
├── markers/aruco_3.png (200x200, 98% quality)
└── markers/markers_A4.pdf (Print ready)

📏 Physical dimensions:
- Marker size: 67mm x 67mm
- Border: 5mm
- Total: 77mm x 77mm
- Print at 300 DPI for best results
```

### Camera Test Results
```
📹 Camera Test Summary:
✅ Camera /dev/video0 detected
✅ Resolution 1920x1080 @ 30 FPS supported
✅ ArUco detection: 4/4 markers (100%)
✅ Ball detection: 14 ± 1 balls
✅ Processing speed: 38.2 FPS
⚠️  Lighting: Slightly dim (recommend +20% brightness)
🎯 Overall quality: 91/100 (Excellent)
```

---

💡 **Workflow Tip**: Always run `camera_test.py` after hardware changes and `gen_markers.py` when setting up new tables.
