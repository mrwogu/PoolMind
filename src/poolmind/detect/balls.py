import cv2
import numpy as np


class BallDetector:
    def __init__(self, cfg):
        self.hough_dp = cfg.get("hough_dp", 1.2)
        self.hough_min_dist = cfg.get("hough_min_dist", 16)
        self.hough_param1 = cfg.get("hough_param1", 120)
        self.hough_param2 = cfg.get("hough_param2", 18)
        self.ball_min_radius = cfg.get("ball_min_radius", 8)
        self.ball_max_radius = cfg.get("ball_max_radius", 18)

    def detect(self, warped_bgr):
        gray = cv2.cvtColor(warped_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=self.hough_dp,
            minDist=self.hough_min_dist,
            param1=self.hough_param1,
            param2=self.hough_param2,
            minRadius=self.ball_min_radius,
            maxRadius=self.ball_max_radius,
        )
        balls = []
        if circles is not None:
            for x, y, r in np.round(circles[0, :]).astype("int"):
                # Basic color classification (could be enhanced later)
                color_type = self._classify_ball_color(
                    warped_bgr, int(x), int(y), int(r)
                )
                balls.append((int(x), int(y), int(r), color_type))
        return balls

    def _classify_ball_color(self, img, cx, cy, radius):
        """Simple color classification - sample HSV in center region of ball"""
        # Sample smaller region in the center of the ball
        sample_r = max(3, radius // 3)
        y1, y2 = max(0, cy - sample_r), min(img.shape[0], cy + sample_r)
        x1, x2 = max(0, cx - sample_r), min(img.shape[1], cx + sample_r)

        roi = img[y1:y2, x1:x2]
        if roi.size == 0:
            return "unknown"

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mean_h, mean_s, mean_v = cv2.mean(hsv)[:3]

        # Simple heuristic classification
        if mean_v > 200 and mean_s < 50:  # High brightness, low saturation
            return "cue"  # likely white cue ball
        elif mean_s > 100:  # High saturation indicates colored ball
            if mean_h < 30 or mean_h > 150:  # Red range
                return "solid"
            elif 40 < mean_h < 80:  # Green/Yellow range
                return "solid"
            else:
                return "stripe"
        else:
            return "unknown"
