import cv2
import numpy as np


class Overlay:
    def __init__(self, cfg, table):
        self.show_fps = cfg.get("show_fps", True)
        self.draw_ids = cfg.get("draw_ids", True)
        self.draw_trails = cfg.get("draw_trails", True)
        self.table = table
        self.trails = {}

    def draw(self, frame_bgr, warped_bgr, H_inv, tracks, fps, dbg_markers):
        out = frame_bgr.copy()

        # draw marker diagnostics
        if dbg_markers is not None:
            corners, ids = dbg_markers
            cv2.aruco.drawDetectedMarkers(out, corners, ids)

        # draw tracks in warped space then back-project
        for oid, track_data in tracks.items():
            # Handle both old (x,y,r) and new (x,y,r,color) formats
            if len(track_data) >= 4:
                x, y, _, color = track_data
            else:
                x, y, _, color = track_data[0], track_data[1], track_data[2], "unknown"

            if self.draw_trails:
                self.trails.setdefault(oid, [])
                self.trails[oid].append((x, y))
                self.trails[oid] = self.trails[oid][-60:]

        # back project centers to original frame
        centers = np.array(
            [[track_data[0], track_data[1]] for track_data in tracks.values()],
            dtype=np.float32,
        )
        back_pts = (
            self.table.back_project_points(centers, H_inv) if len(centers) > 0 else []
        )

        for i, (oid, track_data) in enumerate(tracks.items()):
            if len(track_data) >= 4:
                x, y, _, color = track_data
            else:
                x, y, _, color = track_data[0], track_data[1], track_data[2], "unknown"

            if len(back_pts) > i:
                bx, by = map(int, back_pts[i])

                # Color-coded circles
                circle_color = self._get_ball_color(color)
                cv2.circle(out, (bx, by), 12, circle_color, 2)

                if self.draw_ids:
                    label = f"ID {oid}"
                    if color != "unknown":
                        label += f" ({color})"
                    cv2.putText(
                        out,
                        label,
                        (bx + 10, by - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        circle_color,
                        2,
                        cv2.LINE_AA,
                    )

        # FPS
        if self.show_fps:
            cv2.putText(
                out,
                f"{fps:5.1f} FPS",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

        return out

    def _get_ball_color(self, color_type):
        """Return BGR color for different ball types"""
        color_map = {
            "cue": (255, 255, 255),  # White
            "solid": (0, 255, 0),  # Green
            "stripe": (255, 0, 0),  # Blue
            "unknown": (0, 255, 255),  # Yellow
        }
        return color_map.get(color_type, (0, 255, 255))

    def draw_pockets(self, out, h_matrix=None):
        # draw pocket hints by projecting canonical pocket centers to original frame
        if h_matrix is None:
            return

        pockets = self.table.default_pockets(20)
        if len(pockets) == 0:
            return

        pts = np.array([[x, y] for (x, y, _) in pockets], dtype=np.float32)
        if len(pts) == 0:
            return

        pts_h = np.hstack([pts, np.ones((len(pts), 1))])
        prj = (h_matrix @ pts_h.T).T
        prj = prj[:, :2] / prj[:, [2]]
        for x, y in prj.astype(int):
            cv2.circle(out, (x, y), 10, (0, 120, 255), 2)
