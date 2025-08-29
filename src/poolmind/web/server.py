import asyncio
import os
import time
from typing import Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="PoolMind", description="Real-time Pool Vision System")
hub = None  # injected

# Get the directory of this file to properly resolve paths
current_dir = os.path.dirname(os.path.abspath(__file__))

# Mount static files
static_dir = os.path.join(current_dir, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Setup templates
templates_dir = os.path.join(current_dir, "templates")
templates: Optional[Jinja2Templates] = None
if os.path.exists(templates_dir):
    templates = Jinja2Templates(directory=templates_dir)

# Templates configuration completed above


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if templates:
        return templates.TemplateResponse("index.html", {"request": request})
    else:
        # Fallback to basic HTML if templates directory doesn't exist
        return HTMLResponse(
            """
        <!DOCTYPE html>
        <html>
        <head><title>PoolMind</title></head>
        <body>
            <h1>PoolMind</h1>
            <p>Templates not found. Please check the templates directory.</p>
            <a href="/stream.mjpg">View Stream</a>
        </body>
        </html>
        """
        )


@app.get("/stream.mjpg")
async def stream():
    async def gen():
        boundary = "frame"
        placeholder_text = "Camera not available"
        while True:
            if hub is not None:
                buf = hub.get_jpeg(quality=75)
                if buf is not None:
                    yield (
                        b"--" + boundary.encode() + b"\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: "
                        + str(len(buf)).encode()
                        + b"\r\n\r\n"
                        + buf
                        + b"\r\n"
                    )
                else:
                    # Create simple placeholder image if hub returns None
                    import cv2
                    import numpy as np

                    img = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(
                        img,
                        placeholder_text,
                        (200, 240),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (255, 255, 255),
                        2,
                    )
                    _, buf = cv2.imencode(".jpg", img)
                    buf = buf.tobytes()
                    yield (
                        b"--" + boundary.encode() + b"\r\n"
                        b"Content-Type: image/jpeg\r\n"
                        b"Content-Length: "
                        + str(len(buf)).encode()
                        + b"\r\n\r\n"
                        + buf
                        + b"\r\n"
                    )
            else:
                # Create simple placeholder image if no hub
                import cv2
                import numpy as np

                img = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(
                    img,
                    placeholder_text,
                    (200, 240),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    2,
                )
                _, buf = cv2.imencode(".jpg", img)
                buf = buf.tobytes()
                yield (
                    b"--" + boundary.encode() + b"\r\n"
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: "
                    + str(len(buf)).encode()
                    + b"\r\n\r\n"
                    + buf
                    + b"\r\n"
                )
            await asyncio.sleep(0.1)

    return StreamingResponse(
        gen(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@app.get("/state")
async def state():
    if hub is not None:
        try:
            snapshot_result = hub.snapshot()
            if snapshot_result and len(snapshot_result) >= 2:
                _, s, _ = snapshot_result
                return JSONResponse(s or {})
        except Exception:
            pass

    # Return default state when no camera available or error
    return JSONResponse(
        {
            "cue_balls": 0,
            "solid_balls": 0,
            "stripe_balls": 0,
            "total_balls": 0,
            "game_state": "waiting",
            "current_player": 1,
            "total_tracked": 0,
            "active_balls": 0,
            "potted": 0,
            "active_cue": 0,
            "active_solid": 0,
            "active_stripe": 0,
            "cue_potted": 0,
            "solid_potted": 0,
            "stripe_potted": 0,
        }
    )


@app.get("/events")
async def events():
    if hub is not None:
        try:
            snapshot_result = hub.snapshot()
            if snapshot_result and len(snapshot_result) >= 3:
                _, _, evs = snapshot_result
                # Sort events by timestamp in descending order (most recent first)
                if evs:
                    sorted_events = sorted(
                        evs, key=lambda x: x.get("ts", 0), reverse=True
                    )
                    return JSONResponse(sorted_events)
                return JSONResponse([])
        except Exception:
            pass
    return JSONResponse([])


@app.get("/frame.jpg")
async def frame():
    if hub is not None:
        buf = hub.get_jpeg(quality=80)
        if buf is not None:
            return Response(content=buf, media_type="image/jpeg")

    # Create placeholder image
    import cv2
    import numpy as np

    img = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(
        img, "No camera", (250, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
    )
    _, buf = cv2.imencode(".jpg", img)
    # Handle both numpy array and bytes (for testing)
    if hasattr(buf, "tobytes"):
        return Response(content=buf.tobytes(), media_type="image/jpeg")
    else:
        return Response(content=buf, media_type="image/jpeg")


@app.get("/config")
async def get_config():
    """Get current configuration summary"""
    return JSONResponse(
        {
            "camera": {"width": 1280, "height": 720, "fps": 30},
            "detection": {"method": "HoughCircles"},
            "calibration": {"markers": "ArUco 4x4_50"},
            "web": {"version": "1.0"},
        }
    )


@app.get("/markers/download")
async def download_markers():
    """Download the generated markers PDF"""
    import os

    markers_pdf = "markers/markers_A4.pdf"
    if os.path.exists(markers_pdf):
        with open(markers_pdf, "rb") as f:
            content = f.read()
            return Response(
                content=content,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=markers_A4.pdf"},
            )
    return Response(status_code=404)


@app.post("/game/reset")
async def reset_game():
    """Reset the current game"""
    return JSONResponse({"status": "game reset", "message": "Game reset requested"})


@app.get("/health")
async def health_check():
    """Health check endpoint for production monitoring"""
    try:
        # Check if hub is available and responsive
        if hub is not None:
            # Try to get a snapshot to verify hub is working
            _, state, _ = hub.snapshot()
            hub_status = "healthy"
            hub_data = state if state else {}
        else:
            hub_status = "no_hub"
            hub_data = {}

        return JSONResponse(
            {
                "status": "healthy",
                "timestamp": time.time(),
                "components": {
                    "web_server": "healthy",
                    "hub": hub_status,
                    "last_frame_time": hub_data.get("timestamp", None),
                },
                "version": "1.0.0",
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e),
                "version": "1.0.0",
            },
        )


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        metrics_data = []

        # Basic application metrics
        metrics_data.append(
            "# HELP poolmind_uptime_seconds Application uptime in seconds"
        )
        metrics_data.append("# TYPE poolmind_uptime_seconds counter")
        metrics_data.append(f"poolmind_uptime_seconds {time.time()}")

        if hub is not None:
            _, state, events = hub.snapshot()

            if state:
                # Camera connectivity
                metrics_data.append(
                    "# HELP poolmind_camera_connected Camera connection status"
                )
                metrics_data.append("# TYPE poolmind_camera_connected gauge")
                camera_connected = 1 if state.get("camera_connected", False) else 0
                metrics_data.append(f"poolmind_camera_connected {camera_connected}")

                # Ball detection metrics
                metrics_data.append(
                    "# HELP poolmind_balls_detected Total balls currently detected"
                )
                metrics_data.append("# TYPE poolmind_balls_detected gauge")
                active_balls = state.get("active_balls", 0)
                metrics_data.append(f"poolmind_balls_detected {active_balls}")

                # Frame processing time
                help_text = "# HELP poolmind_frame_processing_time_seconds Frame processing time"
                metrics_data.append(help_text)
                metrics_data.append(
                    "# TYPE poolmind_frame_processing_time_seconds gauge"
                )
                processing_time = state.get("processing_time", 0)
                metrics_data.append(
                    f"poolmind_frame_processing_time_seconds {processing_time}"
                )

                # Detection accuracy
                help_text = "# HELP poolmind_detection_accuracy_percent Detection accuracy percent"
                metrics_data.append(help_text)
                metrics_data.append("# TYPE poolmind_detection_accuracy_percent gauge")
                detection_accuracy = state.get("detection_accuracy", 0)
                metrics_data.append(
                    f"poolmind_detection_accuracy_percent {detection_accuracy}"
                )

            # Event metrics
            if events:
                metrics_data.append(
                    "# HELP poolmind_events_total Total number of game events"
                )
                metrics_data.append("# TYPE poolmind_events_total counter")
                metrics_data.append(f"poolmind_events_total {len(events)}")

        content = "\n".join(metrics_data) + "\n"
        return Response(content=content, media_type="text/plain")
    except Exception as e:
        return Response(
            status_code=500,
            content=f"# Error generating metrics: {str(e)}\n",
            media_type="text/plain",
        )


def set_hub(hub_instance):
    global hub
    hub = hub_instance
