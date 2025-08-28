import os
import subprocess
import time

import cv2
import numpy as np


class ReplayRecorder:
    def __init__(self, cfg, cam_cfg):
        self.enabled = cfg.get("enabled", True)
        self.threshold = cfg.get("diff_threshold", 18.0)
        self.cooldown_frames = cfg.get("cooldown_frames", 60)
        self.clip_seconds = cfg.get("clip_seconds", 12)
        self.outdir = cfg.get("output_dir", "replays")
        os.makedirs(self.outdir, exist_ok=True)

        self.prev_gray = None
        self.cooldown = 0

        self.width = cam_cfg.get("width", 1280)
        self.height = cam_cfg.get("height", 720)
        self.fps = cam_cfg.get("fps", 30)

    def process_frame(self, frame_bgr):
        if not self.enabled:
            return
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        if self.prev_gray is None:
            self.prev_gray = gray
            return
        diff = cv2.absdiff(gray, self.prev_gray)
        self.prev_gray = gray
        score = diff.mean()

        if self.cooldown > 0:
            self.cooldown -= 1
            return

        if score > self.threshold:
            # record short clip via ffmpeg from V4L2 (best-effort)
            ts = time.strftime("%Y%m%d-%H%M%S")
            outfile = os.path.join(self.outdir, f"replay-{ts}.mp4")
            # This command assumes the camera is /dev/video0; adjust if needed.
            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "v4l2",
                "-framerate",
                str(self.fps),
                "-video_size",
                f"{self.width}x{self.height}",
                "-i",
                "/dev/video0",
                "-t",
                str(self.clip_seconds),
                "-vcodec",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                outfile,
            ]
            try:
                subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                self.cooldown = self.cooldown_frames
            except Exception:
                pass
