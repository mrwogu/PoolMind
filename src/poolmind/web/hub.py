import threading
import time
from collections import deque

import cv2
import numpy as np


class FrameHub:
    def __init__(self, max_events=200):
        self.lock = threading.Lock()
        self.frame_bgr = None  # latest original frame with overlay
        self.state = {}  # dict of stats
        self.events = deque(maxlen=max_events)

    def update_frame(self, frame_bgr, state=None):
        with self.lock:
            self.frame_bgr = frame_bgr
            if state is not None:
                self.state = state

    def push_event(self, ev):
        with self.lock:
            ev = dict(ev)
            ev["ts"] = time.time()
            self.events.append(ev)

    def get_jpeg(self, quality=80):
        with self.lock:
            if self.frame_bgr is None:
                return None
            ok, buf = cv2.imencode(
                ".jpg", self.frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            )
            if not ok:
                return None
            return bytes(buf)

    def snapshot(self):
        with self.lock:
            return (
                None if self.frame_bgr is None else self.frame_bgr.copy(),
                dict(self.state),
                list(self.events),
            )
