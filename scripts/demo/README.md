# 🎮 PoolMind Demo Scripts - Physics Simulation Suite

Interactive demonstrations and simulations for testing PoolMind with advanced physics simulation.

## 📋 Physics Simulation Scripts

| Script | Purpose | Features | Hardware Required |
|--------|---------|----------|-------------------|
| [`physics_simulator.py`](physics_simulator.py) | **Advanced Physics** | Full ball physics, collisions, pockets | None |
| [`enhanced_simulation.py`](enhanced_simulation.py) | **Complete Integration** | Physics + PoolMind pipeline + scenarios | None |
| [`simple_physics_demo.py`](simple_physics_demo.py) | **Lightweight Demo** | Basic physics, no dependencies | None |
| [`replay_system.py`](replay_system.py) | **Analysis & Replay** | Record/replay sequences, analytics | None |

## 🎱 Advanced Physics Features

### ✅ **Milestone 1: Ball Physics**
- Realistic velocity vectors and momentum
- Friction and gradual deceleration
- Ball-to-ball elastic collisions
- Energy conservation and transfer

### ✅ **Milestone 2: Wall Bounces**
- Table boundary collision detection
- Angle-preserving reflections
- Energy loss on wall impacts
- Corner collision handling

### ✅ **Milestone 3: Pocket System**
- 6 realistic pocket positions
- Proximity-based "suction" effect
- Ball removal when potted
- Visual feedback system

### ✅ **Milestone 4: Interactive Cue**
- Mouse-based aiming system
- Visual trajectory preview
- Variable force application
- Multiple input methods

### ✅ **Milestone 5: Training Scenarios**
- Multiple practice setups
- Scenario switching system
- Position validation
- Training-specific arrangements

## 🚀 Quick Start

### Advanced Physics Simulation
```bash
export PYTHONPATH="$(pwd)/../../src"
python physics_simulator.py
```

**Controls:**
- `Left Click + Drag`: Aim cue stick
- `1-5`: Force presets
- `SPACE`: Random shot
- `R`: Reset balls
- `Q/ESC`: Quit

### Complete Integration Demo
```bash
export PYTHONPATH="$(pwd)/../../src"
python enhanced_simulation.py
```

**Additional Controls:**
- `SPACE`: Pause/Resume
- `N/P`: Next/Previous scenario
- `D`: Toggle debug overlay

### Simple Physics (No Dependencies)
```bash
python simple_physics_demo.py
```

### Virtual Table Generator

Generate synthetic pool table frames:

```bash
./virtual_table.py
```

**Capabilities:**
- Photorealistic table rendering
- Configurable ball positions
- ArUco marker placement
- Export frames for testing
- Animation sequences

### Full Game Simulation

Complete game simulation with AI players:

```bash
./full_simulation.py
```

**Includes:**
- Complete 8-ball pool game
- AI shot planning
- Physics simulation
- Score tracking
- Game event logging

## 🎯 Demo Features

### Main Demo (`demo.py`)

**Core Pipeline Testing:**
- Camera capture simulation
- ArUco homography transformation
- Ball detection and classification
- Centroid tracking with ID persistence
- Game engine state management
- Web interface streaming

**Interactive Controls:**
- `q` - Quit demo
- `r` - Reset ball positions
- `p` - Pot random ball
- `SPACE` - Pause/resume
- `s` - Save current frame

**Configuration:**
Uses `config/config.yaml` with demo overrides:
```yaml
demo:
  table_size: [1920, 1080]
  ball_count: 16
  fps: 30
  noise_level: 0.1
```

### Simple Demo (`simple_demo.py`)

**Focused Testing:**
- Isolated computer vision components
- Performance profiling
- Parameter tuning interface
- Visual debugging aids

**Use Cases:**
- New developer onboarding
- Algorithm experimentation
- Performance optimization
- Educational demonstrations

### Virtual Table (`virtual_table.py`)

**Synthetic Data Generation:**
- High-quality table rendering
- Realistic lighting and shadows
- Configurable ball arrangements
- Perfect ground truth data

**Applications:**
- Algorithm validation
- Test data generation
- Calibration verification
- Documentation screenshots

## 🔧 Configuration

### Demo Parameters

Edit `config/config.yaml` for demo behavior:

```yaml
demo:
  # Table rendering
  table_size: [1920, 1080]     # Virtual table resolution
  ball_radius: 25              # Ball size in pixels
  fps: 30                      # Simulation frame rate

  # Ball behavior
  ball_count: 16               # Number of balls
  movement_speed: 2.0          # Animation speed
  noise_level: 0.1             # Detection noise

  # Visual settings
  show_debug: true             # Debug overlays
  show_tracking: true          # Tracking trails
  show_homography: true        # Transformation grid

  # Web interface
  enable_web: true             # Start web server
  web_port: 8000              # Server port
```

### Virtual Table Customization

```python
# In virtual_table.py
table = VirtualTable(
    size=(1920, 1080),           # Table dimensions
    felt_color=(34, 139, 34),    # Table felt color (BGR)
    rail_color=(139, 69, 19),    # Rail color (BGR)
    pocket_radius=50,            # Pocket size
    marker_size=100              # ArUco marker size
)

# Customize ball arrangement
table.arrange_balls("triangle")  # "triangle", "line", "random", "custom"
```

## 📊 Performance Analysis

### Benchmarking

All demos include performance metrics:

```
📊 Performance Stats:
Frame Rate: 29.8 FPS
Detection Time: 12.3ms
Tracking Time: 3.1ms
Homography Time: 8.7ms
Total Pipeline: 24.1ms
```

### Profiling

Enable detailed profiling:

```bash
# Run with profiling
python -m cProfile -o demo.prof demo.py

# Analyze results
python -c "import pstats; pstats.Stats('demo.prof').sort_stats('cumulative').print_stats(20)"
```

### Memory Usage

Monitor memory consumption:

```bash
# Memory profiling
python -m memory_profiler demo.py

# Or use system tools
top -p $(pgrep -f demo.py)
```

## 🔍 Debugging Features

### Visual Debugging

Enable debug overlays:

```python
# In demo configuration
debug:
  show_detection_circles: true    # Ball detection circles
  show_tracking_trails: true      # Ball movement trails
  show_homography_grid: true      # Perspective grid
  show_marker_corners: true       # ArUco corner points
  show_color_masks: true          # HSV color filtering
  show_fps_counter: true          # Performance metrics
```

### Frame Export

Save frames for analysis:

```bash
# Export current frame
press 's' during demo

# Batch export
./demo.py --export-frames ./debug_frames/

# Export with annotations
./demo.py --export-annotated
```

### Step-by-Step Mode

Debug pipeline stages:

```bash
./demo.py --step-mode
```

Each frame requires keypress to proceed, allowing detailed inspection.

## 🎓 Educational Use

### Learning Computer Vision

Demos are designed for educational purposes:

1. **Start with simple_demo.py** - Learn basic concepts
2. **Progress to virtual_table.py** - Understand synthetic data
3. **Use demo.py** - See complete pipeline
4. **Try full_simulation.py** - Explore game logic

### Experimentation

Safe environment for testing:

- No hardware requirements
- Repeatable scenarios
- Known ground truth
- Easy parameter adjustment
- Immediate visual feedback

### Algorithm Development

Test new algorithms:

```python
# Add custom detector to demo.py
class CustomBallDetector:
    def detect(self, frame):
        # Your algorithm here
        return detected_balls

# Integrate and compare results
```

## 🐛 Common Issues

### Import Errors

```bash
# Ensure PYTHONPATH is set
export PYTHONPATH="$(pwd)/../../src"

# Verify installation
python -c "import poolmind; print('✅ Import OK')"
```

### Display Issues

```bash
# On headless systems
export DISPLAY=:0

# Or run without display
./demo.py --headless

# Use VNC for remote display
vncviewer localhost:5901
```

### Performance Issues

```bash
# Reduce resolution
./demo.py --resolution 640x480

# Lower frame rate
./demo.py --fps 15

# Disable debug overlays
./demo.py --no-debug
```

---

💡 **Tip**: Start with `demo.py` for a complete overview, then explore specific components with other scripts.
