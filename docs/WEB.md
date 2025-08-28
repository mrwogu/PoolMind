# Web panel (FastAPI)

- Endpoints:
  - `/` — simple HTML panel with MJPEG preview and status
  - `/stream.mjpg` — MJPEG stream (~10 FPS, `web.mjpeg_fps` config affects client loop)
  - `/frame.jpg` — single JPEG frame
  - `/state` — JSON with game state/statistics
  - `/events` — JSON with recent events

Panel starts automatically (background thread) if `web.enabled: true` in `config/config.yaml`. Default: `0.0.0.0:8000`.
