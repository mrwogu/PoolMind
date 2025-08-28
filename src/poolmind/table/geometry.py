import cv2
import numpy as np


class TableGeometry:
    def __init__(self, cfg):
        self.w = cfg.get("table_w", 2000)
        self.h = cfg.get("table_h", 1000)
        self.margin = cfg.get("margin", 30)

    def warp(self, frame, H):
        return cv2.warpPerspective(frame, H, (self.w, self.h))

    def back_project_points(self, pts, H_inv):
        if H_inv is None or len(pts) == 0:
            return []
        pts_h = np.hstack([pts, np.ones((len(pts), 1))])
        prj = (H_inv @ pts_h.T).T
        prj = prj[:, :2] / prj[:, [2]]
        return prj

    def default_pockets(self, r):
        # 6 pockets: 4 corners + 2 middles on longer rails, in canonical space
        w, h = self.w, self.h
        m = self.margin
        pockets = [
            (m, m, r),  # TL
            (w // 2, m, r),  # TM
            (w - m, m, r),  # TR
            (w - m, h - m, r),  # BR
            (w // 2, h - m, r),  # BM
            (m, h - m, r),  # BL
        ]
        return pockets
