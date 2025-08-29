import argparse
import time

import cv2
import yaml

from .calib.markers import MarkerHomography
from .capture.camera import Camera
from .detect.balls import BallDetector
from .game.engine import GameEngine
from .services.replay import ReplayRecorder
from .table.geometry import TableGeometry
from .track.tracker import CentroidTracker
from .ui.overlay import Overlay
from .web.hub import FrameHub


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=str, default="config/config.yaml")
    return ap.parse_args()


def main():
    args = parse_args()
    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    cam_cfg = cfg["camera"]
    cap = Camera(
        index=cam_cfg["index"],
        width=cam_cfg["width"],
        height=cam_cfg["height"],
        fps=cam_cfg["fps"],
    )

    calib = MarkerHomography(cfg["calibration"])
    table = TableGeometry(cfg["calibration"])
    detector = BallDetector(cfg["detection"])
    tracker = CentroidTracker(cfg["tracking"])
    overlay = Overlay(cfg["ui"], table)
    replay = ReplayRecorder(cfg["replay"], cam_cfg)
    engine = GameEngine(table, cfg.get("game", {}))
    hub = FrameHub()

    win = "PoolMind"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    if cfg["ui"].get("fullscreen", True):
        cv2.setWindowProperty(win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    prev = time.time()
    fps = 0.0

    # Start web server (FastAPI) in background if enabled
    web_cfg = cfg.get("web", {})
    if web_cfg.get("enabled", True):
        import threading

        from .web import server as webserver

        webserver.hub = hub

        def run_web():
            import uvicorn

            uvicorn.run(
                webserver.app,
                host=web_cfg.get("host", "0.0.0.0"),
                port=int(web_cfg.get("port", 8000)),
                log_level="warning",
            )

        threading.Thread(target=run_web, daemon=True).start()

    for frame in cap.frames():
        now = time.time()
        dt = now - prev
        prev = now
        fps = 0.9 * fps + 0.1 * (1.0 / dt) if dt > 0 else fps

        H, H_inv, dbg_mrk = calib.homography_from_frame(frame)
        warped = table.warp(frame, H) if H is not None else None

        balls = []
        if warped is not None:
            balls = detector.detect(warped)  # list of (cx, cy, radius)
            tracks = tracker.update(balls)  # dict: id -> (cx, cy, radius)
        else:
            tracks = {}

        # Update game engine
        engine.update(tracks)
        state = engine.get_state()
        out = overlay.draw(frame, warped, H_inv, tracks, fps, dbg_mrk)
        # Optionally draw pockets hints
        if H is not None:
            overlay.draw_pockets(out, H_inv)
        # Publish to web hub
        hub.update_frame(out, state)
        # Push engine events to hub
        for ev in engine.consume_events():
            hub.push_event(ev)

        replay.process_frame(frame)

        cv2.imshow(win, out)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
