# PoolMind - AI Coding Guidelines

## Project Architecture

This is a **computer vision pool assistant** for Raspberry Pi that provides real-time ball tracking, game analysis, and web interface using OpenCV and FastAPI.

**Project Structure Convention:**
- All Python modules use relative imports within `src/poolmind/`
- Configuration driven via `config/config.yaml` YAML file
- Scripts in `scripts/` directory are standalone entry points
- Use `.venv` virtual environment with `source .venv/bin/activate`

**Commit Message Convention:**
This project uses **Conventional Commits** specification. All commit messages MUST follow this format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Required commit types:**
- `feat`: new feature for the user
- `fix`: bug fix for the user
- `docs`: documentation changes
- `style`: code formatting (no logic changes)
- `refactor`: code refactoring (no new features or fixes)
- `test`: adding or modifying tests
- `chore`: dependency updates, configuration, tools
- `perf`: performance improvements
- `ci`: CI/CD pipeline changes
- `build`: build system changes
- `revert`: revert previous changes

**Examples:**
```bash
feat: add real-time ball trajectory prediction
fix: resolve camera initialization timeout on Pi 4
docs: update ArUco marker calibration guide
refactor: extract color detection into separate module
test: add unit tests for centroid tracking algorithm
chore: update OpenCV to version 4.8.1
```

**Pre-commit validation:** Gitlint automatically validates commit messages format before each commit.

**Critical Commit Rules:**
- **NEVER use `git commit --no-verify`** - this bypasses essential quality checks
- **ALWAYS fix all pre-commit hook errors** before committing:
  - Fix import sorting (isort)
  - Fix code formatting (black)
  - Fix linting issues (flake8)
  - Address security issues (bandit) if critical
  - Fix docstring issues (pydocstyle) when adding new public APIs
- **Run tests before committing:** `python -m pytest tests/ -x`
- **If pre-commit hooks fail:** fix the issues, not the process
- **Quality over speed:** proper commits prevent CI/CD failures and technical debt

## Key Patterns & Conventions

### Configuration-Driven Architecture
Every component accepts a `cfg` parameter (dict from YAML):
```python
detector = BallDetector(cfg["detection"])
tracker = CentroidTracker(cfg["tracking"])
engine = GameEngine(table, cfg.get("game", {}))
```

### Component Communication via Hub Pattern
- `web.hub.FrameHub` - Central message broker for frames and game state
- Components publish events: `hub.update_frame(frame, state)`, `hub.push_event(event)`
- Web interface consumes via: `hub.get_jpeg()`, `hub.snapshot()`

### Computer Vision Pipeline
1. **ArUco Homography**: Detect corner markers (IDs 0,1,2,3) for perspective correction
2. **Warped Detection**: All ball detection happens on bird's-eye view using `table.warp(frame, H)`
3. **HSV Classification**: Balls classified by HSV color ranges in warped space
4. **Centroid Tracking**: ID persistence across frames with disappearance counting

### Game Engine Events
Game engine produces discrete events consumed by web interface:
```python
for ev in engine.consume_events():
    hub.push_event(ev)  # {"type": "ball_potted", "ball_id": 5, ...}
```

## Development Workflows

### Running Without Hardware
Use `scripts/demo/demo.py` for testing without camera - creates synthetic frames and tests game engine logic.

### Configuration Tuning
Edit `config/config.yaml` for:
- **HSV ranges** for ball color detection (`detection.hsv_*`)
- **HoughCircles parameters** (`detection.hough_*`)
- **Tracking sensitivity** (`tracking.max_disappeared`)
- **Game logic** (`game.pocket_radius`, `game.disappear_for_pot`)

### Web Development
FastAPI server runs in background thread when `web.enabled: true`. Access endpoints:
- `/` - Dashboard HTML
- `/stream.mjpg` - MJPEG video stream
- `/state` - JSON game state
- `/events` - JSON recent events

### Adding New Detectors
1. Create class in `detect/` with `detect(warped_frame)` method returning `[(x,y,radius), ...]`
2. Register in `game/engine.py` pipeline
3. Add configuration section to `config/config.yaml`

## Critical Implementation Details

### Thread Safety
- Camera capture runs in separate thread via `Camera.frames()` generator
- Web server runs in daemon thread started from main loop
- Use `hub` pattern for cross-thread communication

### Error Handling Philosophy
Components gracefully degrade when hardware unavailable (e.g., no camera returns synthetic frames in demo mode).

### ArUco Marker Requirements
- **Exact placement**: Corner IDs must be 0 (top-left), 1 (top-right), 2 (bottom-right), 3 (bottom-left)
- **Print quality critical**: Use `scripts/tools/gen_markers.py` with high DPI
- **EMA smoothing**: Homography uses exponential moving average for stability (`calibration.ema_alpha`)

### Performance Considerations
- Ball detection only on warped/transformed frames (computationally cheaper)
- Tracking history limited to 120 frames: `self.track_history[oid][-120:]`
- MJPEG streaming quality configurable for bandwidth management

## Computer Vision Pipeline Deep Dive

### ArUco Marker Detection & Homography
```python
# MarkerHomography with EMA smoothing for stability
H, H_inv, debug_markers = calib.homography_from_frame(frame)
warped = table.warp(frame, H) if H is not None else None
```
- **Corner placement critical**: Markers 0,1,2,3 must be clockwise from top-left
- **EMA smoothing**: `calibration.ema_alpha` balances stability vs responsiveness
- **Graceful degradation**: Pipeline continues without markers (returns None)

### Ball Detection Strategy
```python
# HoughCircles on warped frame + HSV color classification
balls = detector.detect(warped)  # [(x,y,radius), ...]
tracks = tracker.update(balls)   # {id: (x,y,radius), ...}
```
**Key parameters in `config.yaml`:**
- `hough_dp`: Accumulator resolution (1.2 = good default)
- `hough_min_dist`: Minimum distance between circles (prevent duplicates)
- `ball_min_radius`/`ball_max_radius`: Physical constraints
- `hsv_green_*`: Table cloth masking ranges

### Tracking & ID Persistence
```python
# CentroidTracker maintains ball identities across frames
self.track_history[oid].append((x,y))
self.disappear_counts[oid] += 1  # Count frames without detection
```
- **Centroid-based**: Associates balls by proximity between frames
- **Disappearance counting**: `max_disappeared` frames before ID removal
- **History buffer**: Last 120 positions for trajectory analysis

## Web Interface Architecture

### Hub-Based Communication
```python
# Central message broker pattern
hub.update_frame(processed_frame, game_state)
hub.push_event({"type": "ball_potted", "ball_id": 5})

# Web endpoints consume hub data
frame_jpeg = hub.get_jpeg(quality=75)
current_state = hub.snapshot()[1]  # (frame, state, events)
```

### FastAPI Endpoints Structure
- **`/stream.mjpg`**: Multipart MJPEG stream with boundary frames
- **`/state`**: JSON game state (ball counts, game phase, scores)
- **`/events`**: Recent game events (potted balls, fouls, etc.)
- **`/frame.jpg`**: Single frame snapshot for debugging

### Real-time Streaming Implementation
```python
async def stream_generator():
    while True:
        jpeg_buffer = hub.get_jpeg()
        yield (b"--frame\r\n" +
               b"Content-Type: image/jpeg\r\n\r\n" +
               jpeg_buffer + b"\r\n")
```

## Development Setup & Workflows

### Environment Setup Commands
```bash
# Initial setup (run once)
./scripts/setup/setup.sh  # Installs dependencies, creates venv, generates markers

# Development activation
source .venv/bin/activate
export PYTHONPATH="$(pwd)/src"

# Testing without hardware
PYTHONPATH=src ./scripts/demo/demo.py

# Web-only development
PYTHONPATH=src python -m uvicorn poolmind.web.server:app --reload
```

### Configuration Tuning Workflow
1. **Camera calibration**: Adjust `camera.resolution` and `fps` for performance
2. **Marker detection**: Tune `calibration.ema_alpha` for homography stability
3. **Ball detection**: Modify `detection.hough_*` parameters for lighting conditions
4. **HSV color ranges**: Update `detection.hsv_green_*` for table cloth masking
5. **Game logic**: Adjust `game.pocket_radius` and `disappear_for_pot` thresholds

### Debugging Strategies
```python
# Visual debugging with overlay
overlay.draw(frame, warped, H_inv, tracks, fps, debug_markers)

# State inspection
print(f"Tracks: {tracks}")  # Current ball positions
print(f"Game state: {engine.get_state()}")  # Game analysis
```

### Adding New Components

**New Ball Detector:**
```python
class CustomDetector:
    def __init__(self, cfg):
        self.cfg = cfg

    def detect(self, warped_frame):
        # Return [(x, y, radius), ...] in warped coordinates
        return detections
```

**New Game Rules:**
```python
class CustomRules:
    def update(self, ball_positions, potted_balls):
        # Return events: [{"type": "foul", "reason": "..."}, ...]
        return events
```

### Hardware Integration Notes
- **Camera device**: Use `v4l2-ctl --list-devices` to find correct index
- **Resolution constraints**: Raspberry Pi camera limits (test with `ffplay`)
- **Performance tuning**: Lower resolution/FPS if CPU usage too high
- **GPIO integration**: Future expansion for physical controls

### Testing & Validation
```bash
# Component testing
PYTHONPATH=src python -c "from poolmind.detect.balls import BallDetector; print('✅ Imports OK')"

# Full pipeline test
PYTHONPATH=src ./scripts/demo/demo.py

# Web interface test
curl http://localhost:8000/state
```

### Production Deployment
```bash
# Systemd service setup
sudo cp scripts/systemd/poolmind.service /etc/systemd/system/
sudo systemctl enable poolmind

# Docker deployment
docker-compose up -d  # Uses multi-stage build for ARM64
```
