# Architecture

```
src/poolmind/
├── app.py                 # main loop: capture → calibrate → warp → detect → track → visualize → (replay)
├── capture/
│   └── camera.py          # threaded camera capture (OpenCV VideoCapture)
├── calib/
│   └── markers.py         # ArUco marker detection + homography EMA smoothing
├── table/
│   └── geometry.py        # canonical table coordinates, pockets, warps
├── detect/
│   └── balls.py           # classic detection (HSV + HoughCircles), color sampling
├── track/
│   └── tracker.py         # simple centroid tracker with ID assignment
├── ui/
│   └── overlay.py         # drawing overlays, scoreboard, trails, FPS
└── services/
    └── replay.py          # motion detector + ffmpeg clips on activity
```

## Pipeline
1. **Capture**: read frames at configured FPS/resolution (USB camera)
2. **Calibration**: detect 4 ArUco markers on table corners → compute homography; smooth over time (EMA)
3. **Warp**: transform to canonical top-down (bird's-eye) view (stable scale & geometry)
4. **Detection**: HoughCircles to find balls (min/max radius tuned to warped space)
5. **Tracking**: centroid tracker to maintain IDs across frames
6. **Game Logic (future)**: pocket zones → disappearances → score events
7. **UI**: draw on original (back-projected) or on warped view; HDMI fullscreen
8. **Replay**: motion → buffer → write short MP4 clips

## Extensibility
- Swap detector for YOLO (TPU/NCS2) under `detect/` without touching the rest
- Add AprilTag backend if ArUco not available
- Log events and trajectories to a SQLite DB for analytics
