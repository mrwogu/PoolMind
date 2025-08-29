#!/usr/bin/env python3
"""
PoolMind Camera Test Tool
Tests camera input and basic computer vision pipeline
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import yaml

# Add src to Python path
sys.path.insert(0, "src")


class CameraTest:
    """
    Test camera input and basic computer vision pipeline
    """

    def __init__(self, config_path="config/config.yaml", camera_id=0):
        print(f"🎱 Initializing Camera Test (camera {camera_id})...")

        # Load configuration
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

        # Camera setup
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)

        if not self.cap.isOpened():
            raise RuntimeError(f"❌ Cannot open camera {camera_id}")

        # Set camera properties from config
        cam_cfg = self.cfg.get("camera", {})
        width = cam_cfg.get("width", 1280)
        height = cam_cfg.get("height", 720)
        fps = cam_cfg.get("fps", 30)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

        # Get actual camera properties
        actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = self.cap.get(cv2.CAP_PROP_FPS)

        print(f"✅ Camera {camera_id} opened successfully:")
        print(f"   Requested: {width}x{height} @ {fps}fps")
        print(f"   Actual: {actual_width}x{actual_height} @ {actual_fps}fps")

        # Stats
        self.frame_count = 0
        self.fps_counter = []

        # Detection modes
        self.show_aruco = True
        self.show_balls = True
        self.show_table_mask = False

    def detect_aruco_markers(self, frame):
        """Detect ArUco markers"""
        try:
            import cv2.aruco as aruco

            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            try:
                parameters = aruco.DetectorParameters()
                detector = aruco.ArucoDetector(aruco_dict, parameters)
                corners, ids, _ = detector.detectMarkers(gray)
            except (AttributeError, TypeError):
                return None, None

            return corners, ids

        except Exception as e:
            print(f"ArUco error: {e}")
            return None, None

    def detect_table_area(self, frame):
        """Detect green table area"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Green range from config
        detection_cfg = self.cfg.get("detection", {})
        green_lower = np.array(detection_cfg.get("hsv_green_lower", [35, 30, 30]))
        green_upper = np.array(detection_cfg.get("hsv_green_upper", [85, 255, 255]))

        mask = cv2.inRange(hsv, green_lower, green_upper)

        # Clean up mask
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        return mask

    def detect_balls(self, frame, table_mask=None):
        """Detect balls using HoughCircles"""
        if table_mask is not None:
            # Apply table mask
            frame_masked = cv2.bitwise_and(frame, frame, mask=table_mask)
            gray = cv2.cvtColor(frame_masked, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # HoughCircles parameters from config
        detection_cfg = self.cfg.get("detection", {})

        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=detection_cfg.get("hough_dp", 1.2),
            minDist=detection_cfg.get("hough_min_dist", 16),
            param1=detection_cfg.get("hough_param1", 120),
            param2=detection_cfg.get("hough_param2", 18),
            minRadius=detection_cfg.get("ball_min_radius", 8),
            maxRadius=detection_cfg.get("ball_max_radius", 18),
        )

        detections = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            for x, y, r in circles:
                detections.append((x, y, r))

        return detections

    def draw_info(self, frame, corners, ids, balls, table_mask, fps):
        """Draw all detection information"""
        h, w = frame.shape[:2]

        # Title
        cv2.putText(
            frame,
            f"PoolMind Camera Test (Cam {self.camera_id})",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )

        # Detection status
        y_pos = 70

        # ArUco markers
        if corners is not None and ids is not None:
            marker_count = len(ids)
            cv2.putText(
                frame,
                f"ArUco Markers: {marker_count}/4",
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            if self.show_aruco:
                try:
                    import cv2.aruco as aruco

                    aruco.drawDetectedMarkers(frame, corners, ids)
                except Exception:
                    pass
        else:
            cv2.putText(
                frame,
                "ArUco Markers: 0/4",
                (10, y_pos),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        y_pos += 30

        # Ball detection
        ball_count = len(balls)
        cv2.putText(
            frame,
            f"Balls Detected: {ball_count}",
            (10, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2,
        )

        if self.show_balls:
            for i, (x, y, r) in enumerate(balls):
                cv2.circle(frame, (x, y), r, (0, 255, 255), 2)
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)
                cv2.putText(
                    frame,
                    str(i + 1),
                    (x - 5, y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 255),
                    1,
                )

        y_pos += 30

        # Table detection
        if table_mask is not None:
            contours, _ = cv2.findContours(
                table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                cv2.putText(
                    frame,
                    f"Table Area: {int(area)}",
                    (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

                if self.show_table_mask:
                    # Show table mask as overlay
                    colored_mask = cv2.applyColorMap(table_mask, cv2.COLORMAP_SPRING)
                    frame = cv2.addWeighted(frame, 0.8, colored_mask, 0.2, 0)

        # FPS and frame count
        cv2.putText(
            frame,
            f"FPS: {fps}",
            (w - 100, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Frame: {self.frame_count}",
            (w - 150, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        # Controls
        controls = [
            "Controls:",
            "A - Toggle ArUco",
            "B - Toggle Balls",
            "T - Toggle Table",
            "S - Save frame",
            "Q - Quit",
        ]

        for i, control in enumerate(controls):
            cv2.putText(
                frame,
                control,
                (10, h - 120 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (200, 200, 200),
                1,
            )

        # Detection modes status
        modes = [
            f"ArUco: {'ON' if self.show_aruco else 'OFF'}",
            f"Balls: {'ON' if self.show_balls else 'OFF'}",
            f"Table: {'ON' if self.show_table_mask else 'OFF'}",
        ]

        for i, mode in enumerate(modes):
            color = (0, 255, 0) if "ON" in mode else (0, 0, 255)
            cv2.putText(
                frame,
                mode,
                (w - 150, 70 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )

    def run_test(self):
        """Run camera test"""
        print("🚀 Starting Camera Test...")
        print("🎮 Controls: A=ArUco, B=Balls, T=Table, S=Save, Q=Quit")

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Failed to read frame")
                    break

                # Calculate FPS
                current_time = time.time()
                self.fps_counter.append(current_time)
                self.fps_counter = [
                    t for t in self.fps_counter if current_time - t < 1.0
                ]
                fps = len(self.fps_counter)

                # Computer vision pipeline
                corners, ids = self.detect_aruco_markers(frame)
                table_mask = self.detect_table_area(frame)
                balls = self.detect_balls(frame, table_mask)

                # Draw results
                self.draw_info(frame, corners, ids, balls, table_mask, fps)

                # Display
                cv2.imshow(f"PoolMind Camera Test - Camera {self.camera_id}", frame)

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q") or key == 27:
                    break
                elif key == ord("a"):
                    self.show_aruco = not self.show_aruco
                    print(f"ArUco display: {'ON' if self.show_aruco else 'OFF'}")
                elif key == ord("b"):
                    self.show_balls = not self.show_balls
                    print(f"Ball display: {'ON' if self.show_balls else 'OFF'}")
                elif key == ord("t"):
                    self.show_table_mask = not self.show_table_mask
                    print(f"Table mask: {'ON' if self.show_table_mask else 'OFF'}")
                elif key == ord("s"):
                    timestamp = int(time.time())
                    filename = f"camera_test_{self.camera_id}_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"💾 Frame saved as {filename}")

                self.frame_count += 1

        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            print("🎯 Camera test finished!")


def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description="PoolMind Camera Test Tool")
    parser.add_argument(
        "--camera", "-c", type=int, default=0, help="Camera device ID (default: 0)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Configuration file path",
    )
    parser.add_argument(
        "--list-cameras", action="store_true", help="List available cameras and exit"
    )

    args = parser.parse_args()

    print("🎱 PoolMind Camera Test Tool")
    print("=" * 40)

    if args.list_cameras:
        print("🔍 Scanning for available cameras...")
        for i in range(10):  # Check first 10 camera IDs
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                print(f"  Camera {i}: {width}x{height} @ {fps}fps")
                cap.release()
        return

    # Check if config exists
    if not Path(args.config).exists():
        print(f"❌ Configuration file not found: {args.config}")
        print("Please run from the PoolMind root directory")
        return

    try:
        # Run camera test
        test = CameraTest(args.config, args.camera)
        test.run_test()
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
