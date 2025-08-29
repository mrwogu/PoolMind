#!/usr/bin/env python3
"""
Simplified PoolMind Demo with Virtual Table
Tests the core computer vision pipeline without complex dependencies
"""
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import yaml

# Add paths for imports
sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from virtual_table import VirtualPoolTable


class SimplePoolMindDemo:
    """
    Simplified demo showing virtual table with basic computer vision
    """

    def __init__(self, config_path="config/config.yaml"):
        print("🎱 Initializing Simple PoolMind Demo...")

        # Load configuration
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

        # Initialize virtual table
        self.virtual_table = VirtualPoolTable(config_path)

        # Stats
        self.frame_count = 0
        self.fps_counter = []

        print("✅ Demo initialized successfully!")

    def detect_balls_simple(self, frame):
        """Simple ball detection using HoughCircles"""
        # Convert to HSV for green table detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Create mask for green table area
        green_lower = np.array([35, 30, 30])
        green_upper = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, green_lower, green_upper)

        # Apply mask to get table area
        table_area = cv2.bitwise_and(frame, frame, mask=mask)
        gray = cv2.cvtColor(table_area, cv2.COLOR_BGR2GRAY)

        # Detect circles (balls)
        circles = cv2.HoughCircles(
            gray,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=20,
            param1=50,
            param2=30,
            minRadius=8,
            maxRadius=25,
        )

        detections = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype(int)
            for x, y, r in circles:
                # Simple color detection
                roi = frame[max(0, y - r) : y + r, max(0, x - r) : x + r]
                if roi.size > 0:
                    avg_color = np.mean(roi, axis=(0, 1))
                    # Classify as cue (white) or colored
                    if np.mean(avg_color) > 200:
                        ball_type = "cue"
                    else:
                        ball_type = "colored"
                    detections.append((x, y, r, ball_type))

        return detections

    def detect_aruco_markers(self, frame):
        """Simple ArUco marker detection with broad compatibility"""
        try:
            import cv2.aruco as aruco

            # ArUco dictionary
            aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Try new OpenCV API first
            try:
                parameters = aruco.DetectorParameters()
                detector = aruco.ArucoDetector(aruco_dict, parameters)
                corners, ids, _ = detector.detectMarkers(gray)
                return corners, ids
            except (AttributeError, TypeError):
                # New API not available, skip ArUco for now
                # This prevents errors with different OpenCV versions
                return None, None

        except Exception as e:
            # Print error only once per session
            if not hasattr(self, "_aruco_error_shown"):
                print(f"ArUco detection not available: {e}")
                self._aruco_error_shown = True
            return None, None

    def process_frame(self, frame):
        """Process frame through simplified pipeline"""
        processed_frame = frame.copy()

        # Step 1: ArUco marker detection
        corners, ids = self.detect_aruco_markers(frame)

        # Step 2: Ball detection
        ball_detections = self.detect_balls_simple(frame)

        # Step 3: Calculate FPS
        current_time = time.time()
        self.fps_counter.append(current_time)
        self.fps_counter = [t for t in self.fps_counter if current_time - t < 1.0]
        fps = len(self.fps_counter)

        # Step 4: Draw results
        self._draw_results(processed_frame, corners, ids, ball_detections, fps)

        return processed_frame

    def _draw_results(self, frame, corners, ids, ball_detections, fps):
        """Draw detection results on frame"""
        h, w = frame.shape[:2]

        # Draw title
        cv2.putText(
            frame,
            "PoolMind Simple Demo",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 255),
            2,
        )

        # Draw ArUco markers
        if corners is not None and ids is not None:
            try:
                import cv2.aruco as aruco

                aruco.drawDetectedMarkers(frame, corners, ids)

                # Count detected markers
                marker_count = len(ids)
                cv2.putText(
                    frame,
                    f"ArUco Markers: {marker_count}/4",
                    (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            except Exception:
                pass
        else:
            cv2.putText(
                frame,
                "ArUco Markers: 0/4",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        # Draw ball detections
        ball_count = len(ball_detections)
        cv2.putText(
            frame,
            f"Balls Detected: {ball_count}",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2,
        )

        for i, (x, y, r, ball_type) in enumerate(ball_detections):
            # Draw circle around ball
            color = (255, 255, 255) if ball_type == "cue" else (0, 255, 255)
            cv2.circle(frame, (x, y), r, color, 2)
            cv2.circle(frame, (x, y), 2, color, -1)

            # Draw ball ID
            cv2.putText(
                frame,
                str(i + 1),
                (x - 5, y + 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color,
                1,
            )

        # Draw FPS
        cv2.putText(
            frame,
            f"FPS: {fps}",
            (w - 100, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )

        # Draw frame count
        cv2.putText(
            frame,
            f"Frame: {self.frame_count}",
            (w - 150, h - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        # Draw pipeline status
        pipeline_steps = [
            "✅ Virtual Table Generation",
            "✅ ArUco Marker Detection",
            "✅ Ball Detection (HoughCircles)",
            "✅ Results Visualization",
        ]

        for i, step in enumerate(pipeline_steps):
            cv2.putText(
                frame,
                step,
                (10, 140 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 0),
                1,
            )

        # Draw controls
        controls = ["Controls:", "SPACE - Pot ball", "R - Reset", "Q - Quit"]
        for i, control in enumerate(controls):
            cv2.putText(
                frame,
                control,
                (10, h - 80 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (200, 200, 200),
                1,
            )

    def run_demo(self):
        """Run the simplified demo"""
        print("🚀 Starting Simple PoolMind Demo...")
        print("🎮 Controls: SPACE=pot ball, R=reset, Q=quit")

        try:
            while True:
                # Generate virtual table frame
                virtual_frame = self.virtual_table.generate_frame(self.frame_count)

                # Process through simplified pipeline
                processed_frame = self.process_frame(virtual_frame)

                # Display result
                cv2.imshow("PoolMind Simple Demo", processed_frame)

                # Handle keyboard input
                key = cv2.waitKey(30) & 0xFF

                if key == ord("q") or key == 27:  # Quit
                    break
                elif key == ord(" "):  # Pot random ball
                    active_balls = [
                        b
                        for b in self.virtual_table.balls
                        if b["active"] and b["id"] > 0
                    ]
                    if active_balls:
                        rng = np.random.default_rng(int(time.time()))
                        ball_to_pot = rng.choice(active_balls)
                        self.virtual_table.pot_ball(ball_to_pot["id"])
                elif key == ord("r"):  # Reset
                    self.virtual_table.reset_balls()
                    self.frame_count = 0

                self.frame_count += 1

                # Auto-demo: pot balls occasionally
                if self.frame_count % 300 == 0:  # Every 10 seconds
                    active_balls = [
                        b
                        for b in self.virtual_table.balls
                        if b["active"] and b["id"] > 0
                    ]
                    if active_balls and len(active_balls) > 2:
                        rng = np.random.default_rng(int(time.time()) + self.frame_count)
                        ball_to_pot = rng.choice(active_balls)
                        self.virtual_table.pot_ball(ball_to_pot["id"])
                        print(f"🎱 Auto-demo: Ball {ball_to_pot['id']} potted")

        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted by user")

        finally:
            cv2.destroyAllWindows()
            print("🎯 Simple demo finished!")


def main():
    """Main function"""
    print("🎱 PoolMind Simple Demo with Virtual Table")
    print("=" * 50)

    # Check if config exists
    config_path = "config/config.yaml"
    if not Path(config_path).exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("Please run from the PoolMind root directory")
        return

    # Run demo
    demo = SimplePoolMindDemo(config_path)
    demo.run_demo()


if __name__ == "__main__":
    main()
