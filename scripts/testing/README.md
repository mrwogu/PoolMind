# 🧪 Testing Scripts

Scripts for testing, debugging, and validating PoolMind's computer vision pipeline, especially ArUco marker detection.

## 📋 Scripts Overview

| Script | Purpose | Focus Area | Use Case |
|--------|---------|------------|----------|
| [`debug_aruco.py`](debug_aruco.py) | **ArUco debugging** | Marker detection | Troubleshoot detection issues |
| [`debug_markers.py`](debug_markers.py) | **Marker analysis** | Virtual table markers | Validate marker generation |
| [`test_aruco.py`](test_aruco.py) | **ArUco testing** | Detection accuracy | Performance validation |
| [`test_pure_aruco.py`](test_pure_aruco.py) | **Isolated ArUco** | Core algorithm | Algorithm verification |
| [`simple_aruco_test.py`](simple_aruco_test.py) | **Basic ArUco** | Quick validation | Rapid testing |

## 🚀 Usage

### Quick ArUco Validation

Test if ArUco detection is working:

```bash
# Setup environment
source ../.venv/bin/activate
export PYTHONPATH="$(pwd)/../../src"

# Quick test
./simple_aruco_test.py
```

**Expected output:**
- Detection of markers 0, 1, 2, 3
- Homography matrix calculation
- Corner coordinate validation

### Debug ArUco Detection Issues

When markers aren't detected properly:

```bash
./debug_aruco.py
```

**Debugging features:**
- Step-by-step detection process
- Visual marker highlighting
- Parameter sensitivity analysis
- Detection confidence scores
- Corner precision metrics

### Validate Marker Generation

Test virtual table marker placement:

```bash
./debug_markers.py
```

**Validation checks:**
- Marker ID correctness (0,1,2,3)
- Corner positioning accuracy
- Size and orientation verification
- Contrast and visibility analysis

### Comprehensive ArUco Testing

Full test suite for ArUco detection:

```bash
./test_aruco.py
```

**Test scenarios:**
- Multiple lighting conditions
- Various table orientations
- Different camera angles
- Noise and distortion effects
- Performance benchmarking

### Isolated Algorithm Testing

Test ArUco without PoolMind dependencies:

```bash
./test_pure_aruco.py
```

**Pure testing:**
- OpenCV ArUco detection only
- No game logic dependencies
- Minimal configuration
- Raw performance metrics

## 🔍 Debugging Workflows

### Marker Detection Not Working

**Step 1: Quick validation**
```bash
./simple_aruco_test.py
```
*Expected: Should detect 4 markers (IDs 0,1,2,3)*

**Step 2: Detailed debugging**
```bash
./debug_aruco.py --verbose
```
*Check: Corner detection, marker IDs, homography quality*

**Step 3: Marker quality check**
```bash
./debug_markers.py --analyze-quality
```
*Verify: Marker contrast, size, positioning*

**Step 4: Algorithm isolation**
```bash
./test_pure_aruco.py --benchmark
```
*Baseline: Pure OpenCV performance*

### Poor Detection Accuracy

**Parameter tuning workflow:**
```bash
# Test different detection parameters
./debug_aruco.py --adaptive-threshold
./debug_aruco.py --corner-refinement
./debug_aruco.py --polygon-approximation

# Compare results
./test_aruco.py --parameter-sweep
```

### Performance Issues

**Benchmarking workflow:**
```bash
# Measure detection time
./test_aruco.py --benchmark

# Profile with different parameters
./debug_aruco.py --profile

# Compare with baseline
./test_pure_aruco.py --timing
```

## 🔧 Configuration

### ArUco Detection Parameters

Edit detection sensitivity in scripts:

```python
# In debug_aruco.py
aruco_params = cv2.aruco.DetectorParameters_create()
aruco_params.adaptiveThreshWinSizeMin = 3      # Adaptive threshold window
aruco_params.adaptiveThreshWinSizeMax = 23     # Maximum window size
aruco_params.adaptiveThreshWinSizeStep = 10    # Window size step
aruco_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
aruco_params.cornerRefinementWinSize = 5       # Corner refinement window
aruco_params.cornerRefinementMaxIterations = 30
aruco_params.cornerRefinementMinAccuracy = 0.1
```

### Test Scenarios

Configure test conditions:

```python
# In test_aruco.py
test_scenarios = [
    {"lighting": "bright", "angle": 0, "distance": "normal"},
    {"lighting": "dim", "angle": 15, "distance": "close"},
    {"lighting": "mixed", "angle": -10, "distance": "far"},
    {"lighting": "harsh", "angle": 30, "distance": "normal"}
]
```

### Debug Output

Control debugging verbosity:

```bash
# Minimal output
./debug_aruco.py --quiet

# Detailed analysis
./debug_aruco.py --verbose --save-frames

# Full debugging
./debug_aruco.py --debug --save-intermediates
```

## 📊 Test Results Analysis

### Detection Accuracy Metrics

Scripts report various accuracy metrics:

```
🎯 ArUco Detection Results:
Total Frames: 1000
Detected Frames: 987 (98.7%)
Average Markers: 3.94/4
Corner Accuracy: 0.23 pixels RMS
Homography Quality: 0.95 (0-1 scale)
Detection Time: 8.3ms average
```

### Performance Benchmarks

```
⚡ Performance Benchmarks:
Frame Processing: 12.4ms
Marker Detection: 8.3ms
Corner Refinement: 3.1ms
Homography Calc: 1.0ms
Total Pipeline: 24.8ms (40.3 FPS)
```

### Quality Analysis

```
🔍 Marker Quality Analysis:
Marker 0: ✅ Excellent (99.8% confidence)
Marker 1: ✅ Good (95.2% confidence)
Marker 2: ⚠️  Fair (89.1% confidence)
Marker 3: ❌ Poor (73.4% confidence)

Recommendations:
- Improve lighting on marker 3
- Check marker 2 print quality
- Consider repositioning markers
```

## 🛠️ Advanced Testing

### Custom Test Scenarios

Create custom test cases:

```python
# In test_aruco.py
def test_custom_scenario():
    """Test specific lighting/angle combination"""
    table = VirtualTable()
    table.set_lighting("sunset")
    table.set_angle(25)
    table.add_noise(0.15)

    results = run_detection_test(table)
    assert results.accuracy > 0.90
```

### Automated Testing

Run comprehensive test suite:

```bash
# Full test suite
./test_aruco.py --full-suite

# Regression testing
./test_aruco.py --regression-test baseline_results.json

# Continuous testing
watch -n 60 './test_aruco.py --quick'
```

### Integration Testing

Test with real camera:

```bash
# Test with physical markers
./debug_aruco.py --camera 0

# Compare virtual vs real
./test_aruco.py --compare-real-virtual

# Calibration validation
./debug_aruco.py --calibration-check
```

## 🐛 Common Issues & Solutions

### No Markers Detected

**Possible causes:**
- Poor lighting conditions
- Marker print quality
- Camera focus issues
- Parameter configuration

**Debug steps:**
```bash
./debug_aruco.py --show-preprocessing  # Check image quality
./debug_aruco.py --adjust-parameters   # Try different settings
./test_pure_aruco.py --minimal         # Test basic functionality
```

### Inconsistent Detection

**Symptoms:**
- Markers appear/disappear between frames
- Poor homography stability
- Tracking jitter

**Solutions:**
```bash
./debug_aruco.py --stability-test      # Test detection stability
./test_aruco.py --parameter-optimization # Optimize parameters
# Enable EMA smoothing in config.yaml
```

### Poor Performance

**Optimization workflow:**
```bash
./test_aruco.py --benchmark --profile  # Identify bottlenecks
./debug_aruco.py --optimize-params     # Find optimal parameters
./test_pure_aruco.py --minimal         # Compare with baseline
```

## 📚 Test Data

### Synthetic Test Images

Scripts can generate test images:

```bash
# Generate marker test set
./debug_markers.py --generate-test-set

# Create challenge scenarios
./test_aruco.py --generate-challenges

# Export for external testing
./debug_aruco.py --export-test-data ./test_images/
```

### Real-world Validation

Test with physical setup:

```bash
# Capture reference images
./debug_aruco.py --capture-reference

# Validate against ground truth
./test_aruco.py --validate-reference

# Performance comparison
./test_aruco.py --real-vs-virtual
```

---

💡 **Testing Strategy**: Start with `simple_aruco_test.py` for quick validation, then use `debug_aruco.py` for detailed troubleshooting.
