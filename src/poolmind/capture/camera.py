import threading
import time

import cv2


class Camera:
    def __init__(self, index=0, width=1280, height=720, fps=30):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        self.lock = threading.Lock()
        self.frame = None
        self.stopped = False

        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def _loop(self):
        while not self.stopped:
            ok, f = self.cap.read()
            if ok:
                with self.lock:
                    self.frame = f
            else:
                time.sleep(0.005)

    def frames(self):
        while not self.stopped:
            with self.lock:
                f = None if self.frame is None else self.frame.copy()
            if f is not None:
                yield f
            else:
                time.sleep(0.005)

    def release(self):
        self.stopped = True
        self.thread.join(timeout=1.0)
        self.cap.release()
