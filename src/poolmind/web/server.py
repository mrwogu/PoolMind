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
                return JSONResponse(evs or [])
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
    return Response(content=buf.tobytes(), media_type="image/jpeg")


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
    return JSONResponse({"status": "Game reset requested"})


def set_hub(hub_instance):
    global hub
    hub = hub_instance
