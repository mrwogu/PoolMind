# Calibration Guide

This guide covers camera positioning, ArUco marker placement, and system calibration for optimal PoolMind performance.

## Camera Positioning

### Critical Requirements

**Position**: Mount camera **directly above the pool table center**
- Height: 2-3 meters above the table surface
- Angle: **Perfect 90° downward** (bird's-eye view)
- Stability: Secure mounting to prevent movement during play

**Field of View**:
- Full table surface must be visible
- Include space around table edges for marker placement
- Avoid extreme wide-angle that causes distortion at edges

**Lighting**:
- Uniform lighting across the table
- Avoid shadows from overhead fixtures
- Consider LED strip lighting around table perimeter

### Why Overhead Camera?

1. **Perspective Correction**: ArUco markers enable precise homography transformation
2. **No Occlusion**: Players and equipment don't block ball view
3. **Accurate Tracking**: Eliminates perspective distortion for ball positions
4. **Consistent Scale**: Same pixel-to-distance ratio across entire table

> ⚠️ **Warning**: Side-mounted, angled, or multiple camera setups are not supported.

## ArUco Markers

### Printing and Placement
- Print 4 ArUco markers (dictionary 4x4_50) with IDs: 0 (top-left), 1 (top-right), 2 (bottom-right), 3 (bottom-left).
- Use high-quality paper and printer for clean, sharp edges
- Stick them flush with the felt near each corner (non-reflective tape)
- Position them **inside the camera field of view** at all times
- Ensure markers are flat and not warped or curved

### Marker ID Positioning
```
0 -------- 1
|          |
|   TABLE  |
|          |
3 -------- 2
```

## Calibration Steps

1. **Start the application** in fullscreen mode
2. **Verify camera view**: Ensure entire table and all 4 markers are visible
3. **Automatic detection**: The app will detect the 4 markers and compute homography transformation
4. **Validation**: Check that the table perspective is correctly mapped to a rectangular view
5. **Fine-tuning**: If camera moves slightly, homography auto-adjusts with EMA smoothing

### Verification Checklist
- [ ] All 4 ArUco markers detected (green borders in debug view)
- [ ] Table corners properly aligned in warped view
- [ ] Ball detection working across entire table surface
- [ ] No perspective distortion in transformed coordinates

## Troubleshooting

### Common Issues

**Markers not detected:**
- Check camera focus and lighting
- Ensure markers are flat and not warped
- Verify marker IDs match expected positions
- Clean marker surfaces from dust/smudges

**Poor homography transformation:**
- Verify camera is mounted directly overhead (90° angle)
- Check that markers form a proper rectangle
- Ensure adequate distance between camera and table
- Validate lighting uniformity across table

**Camera positioning problems:**
- Height too low: Insufficient field of view
- Height too high: Loss of detail and accuracy
- Angled mounting: Perspective distortion cannot be corrected
- Unstable mount: Constant recalibration issues

### Fallback Options
- Uniform lighting improves detection
- If ArUco is not available, temporarily set `calibration.corner_ids: []` and use manual 4-point selection (TODO), or switch to an AprilTag backend.

### Configuration Parameters

Key settings in `config/config.yaml`:
```yaml
calibration:
  corner_ids: [0, 1, 2, 3]  # ArUco marker IDs
  ema_alpha: 0.1            # Homography smoothing factor
  table_w: 2540             # Table width in mm
  table_h: 1270             # Table height in mm
```
