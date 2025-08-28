# PoolMind - Example Configurations

## Basic Configuration (config/config.yaml)
The default configuration works for most setups. Key parameters to adjust:

### Camera Settings
```yaml
camera:
  index: 0            # Try 1, 2 if /dev/video0 doesn't work
  width: 1280         # Lower for performance: 640, 800
  height: 720         # Lower for performance: 480, 600
  fps: 30             # Lower for performance: 15, 20
```

### Detection Tuning
```yaml
detection:
  # Cloth color masking (HSV ranges)
  hsv_green_lower: [35, 30, 30]   # Adjust for your table's cloth
  hsv_green_upper: [85, 255, 255]
  
  # HoughCircles - most important for ball detection
  hough_param2: 18        # Lower = more circles, higher = fewer circles
  ball_min_radius: 8      # Minimum ball size in pixels (warped space)
  ball_max_radius: 18     # Maximum ball size in pixels (warped space)
  hough_min_dist: 16      # Minimum distance between ball centers
```

### Calibration
```yaml
calibration:
  ema_alpha: 0.2          # Homography smoothing: 0.1 = very smooth, 0.5 = responsive
  table_w: 2000           # Virtual table width after warp
  table_h: 1000           # Virtual table height after warp
```

## Example Configurations

### High Performance (Pi 4)
```yaml
camera:
  width: 1280
  height: 720
  fps: 30
detection:
  hough_param2: 20
  ball_min_radius: 10
  ball_max_radius: 20
```

### Low Performance (Pi 3 or limited resources)
```yaml
camera:
  width: 800
  height: 600
  fps: 15
detection:
  hough_param2: 15
  ball_min_radius: 6
  ball_max_radius: 15
replay:
  enabled: false
```

### Dark/Poor Lighting
```yaml
detection:
  hough_param1: 80        # Lower edge detection threshold
  hough_param2: 12        # Lower circle detection threshold
  hsv_green_lower: [30, 20, 20]   # More permissive color range
  hsv_green_upper: [90, 255, 255]
```

### Bright/High Contrast
```yaml
detection:
  hough_param1: 150       # Higher edge detection threshold
  hough_param2: 25        # Higher circle detection threshold
  hsv_green_lower: [40, 40, 40]   # Tighter color range
  hsv_green_upper: [80, 255, 255]
```

### Small Balls/High Resolution
```yaml
calibration:
  table_w: 3000           # Higher resolution virtual table
  table_h: 1500
detection:
  ball_min_radius: 12
  ball_max_radius: 30
  hough_min_dist: 24
```

## Troubleshooting Parameters

### Too Many False Detections
- Increase `hough_param2` (try 25-30)
- Increase `ball_min_radius`
- Increase `hough_min_dist`
- Tighten HSV color ranges

### Missing Ball Detections
- Decrease `hough_param2` (try 10-15)
- Decrease `ball_min_radius`
- Widen HSV color ranges
- Check lighting and marker placement

### Unstable Calibration
- Decrease `ema_alpha` (try 0.1)
- Ensure markers are clearly visible
- Improve lighting contrast
- Check for reflections on markers

### Poor Web Performance
- Decrease camera resolution
- Disable `replay.enabled`
- Lower `web.mjpeg_fps` (if implemented)

## Hardware-Specific Notes

### USB Camera Issues
```bash
# List available cameras
v4l2-ctl --list-devices

# Check supported formats
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Force specific format if needed
v4l2-ctl --device=/dev/video0 --set-fmt-video=width=1280,height=720,pixelformat=MJPG
```

### Pi Camera Module
If using the Pi Camera module instead of USB:
```python
# In capture/camera.py, replace VideoCapture with:
# from picamera import PiCamera
# (requires additional implementation)
```
