import cv2
import numpy as np

try:
    from cv2 import aruco

    _ARUCO_AVAILABLE = True
except Exception:
    _ARUCO_AVAILABLE = False


class MarkerHomography:
    def __init__(self, cfg):
        self.corner_ids = cfg.get("corner_ids", [0, 1, 2, 3])
        self.table_w = cfg.get("table_w", 2000)
        self.table_h = cfg.get("table_h", 1000)
        self.alpha = cfg.get("ema_alpha", 0.2)
        self.H = None
        self.H_inv = None
        if _ARUCO_AVAILABLE:
            self.dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
            self.params = aruco.DetectorParameters_create()
        self._dst_pts = np.array(
            [
                [0, 0],
                [self.table_w - 1, 0],
                [self.table_w - 1, self.table_h - 1],
                [0, self.table_h - 1],
            ],
            dtype=np.float32,
        )

    def homography_from_frame(self, frame):
        dbg = None
        if _ARUCO_AVAILABLE and self.corner_ids:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = aruco.detectMarkers(
                gray, self.dict, parameters=self.params
            )
            if ids is not None and len(ids) >= 4:
                # map id -> center
                id_to_center = {}
                for cs, i in zip(corners, ids.flatten()):
                    c = cs[0]
                    cx = c[:, 0].mean()
                    cy = c[:, 1].mean()
                    id_to_center[int(i)] = (cx, cy)

                if all(i in id_to_center for i in self.corner_ids):
                    src_pts = np.array(
                        [id_to_center[i] for i in self.corner_ids], dtype=np.float32
                    )
                    H = cv2.getPerspectiveTransform(src_pts, self._dst_pts)
                    if self.H is None:
                        self.H = H
                    else:
                        self.H = self._ema_H(self.H, H, self.alpha)
                    self.H_inv = np.linalg.inv(self.H)
                    dbg = (corners, ids)
        return self.H, self.H_inv, dbg

    def _ema_H(self, H_prev, H_new, alpha):
        # Exponential moving average in parameter space by normalizing H
        Hp = H_prev / H_prev[2, 2]
        Hn = H_new / H_new[2, 2]
        Hs = (1.0 - alpha) * Hp + alpha * Hn
        return Hs
