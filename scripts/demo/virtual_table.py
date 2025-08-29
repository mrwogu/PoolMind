#!/usr/bin/env python3
"""
Virtual Pool Table Simulator for PoolMind
Creates synthetic camera frames with ArUco markers and simulated balls
"""
import math
import time
from pathlib import Path

import cv2
import numpy as np
import yaml


class VirtualPoolTable:
    """
    Generates synthetic pool table frames with ArUco markers and balls
    """

    def __init__(self, config_path="config/config.yaml"):
        # Load configuration
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

        # Camera settings
        self.width = self.cfg["camera"]["width"]
        self.height = self.cfg["camera"]["height"]

        # Table dimensions (in pixels on the virtual camera view)
        self.table_margin = 100  # margin around table in frame
        self.table_width = self.width - (2 * self.table_margin)
        self.table_height = int(self.table_width * 0.5)  # Pool table aspect ratio ~2:1

        # Center the table in frame
        self.table_x = self.table_margin
        self.table_y = (self.height - self.table_height) // 2

        # ArUco marker settings
        self.marker_size = 120  # Increased marker size for better detection

        # Generate ArUco markers once
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            self.markers = self._generate_aruco_markers()
            print("   ArUco markers: Generated successfully")
        except Exception as e:
            print(f"   ArUco markers: Failed to generate ({e})")
            self.markers = {}

        # Ball simulation
        self.ball_radius = 12  # ball radius in pixels
        self.balls = self._initialize_balls()

        print("🎱 Virtual Table initialized:")
        print(f"   Frame size: {self.width}x{self.height}")
        print(f"   Table area: {self.table_width}x{self.table_height}")
        print(f"   Markers: {len(self.markers)} ArUco markers")
        print(f"   Balls: {len(self.balls)} simulated balls")

    def _generate_aruco_markers(self):
        """Generate ArUco marker images for IDs 0,1,2,3"""
        markers = {}
        for marker_id in [0, 1, 2, 3]:
            try:
                marker_img = cv2.aruco.generateImageMarker(
                    self.aruco_dict, marker_id, self.marker_size
                )
                # Convert to 3-channel BGR
                marker_bgr = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
                markers[marker_id] = marker_bgr
            except Exception as e:
                print(f"Failed to generate marker {marker_id}: {e}")
                markers[marker_id] = None
        return markers

    def _initialize_balls(self):
        """Initialize ball positions for 8-ball pool with collision detection"""
        balls = []

        # Cue ball (white) - left side
        cue_x = self.table_x + self.table_width // 4
        cue_y = self.table_y + self.table_height // 2
        balls.append(
            {
                "id": 0,
                "type": "cue",
                "color": (255, 255, 255),
                "x": cue_x,
                "y": cue_y,
                "active": True,
            }
        )

        # Rack formation - proper triangle with collision detection
        rack_x = self.table_x + 3 * self.table_width // 4
        rack_y = self.table_y + self.table_height // 2

        # Ball colors for 8-ball pool
        ball_colors = [
            (0, 255, 255),  # 1 - yellow (solid)
            (0, 0, 255),  # 2 - red (solid)
            (255, 0, 0),  # 3 - blue (solid)
            (128, 0, 128),  # 4 - purple (solid)
            (255, 165, 0),  # 5 - orange (solid)
            (0, 128, 0),  # 6 - green (solid)
            (128, 0, 0),  # 7 - maroon (solid)
            (0, 0, 0),  # 8 - black
            (255, 255, 0),  # 9 - yellow stripe
            (255, 0, 255),  # 10 - red stripe
            (255, 255, 255),  # 11 - blue stripe (with stripe pattern)
            (200, 100, 200),  # 12 - purple stripe
            (255, 200, 100),  # 13 - orange stripe
            (100, 255, 100),  # 14 - green stripe
            (200, 100, 100),  # 15 - maroon stripe
        ]

        # Create proper triangle formation without overlaps
        ball_spacing = self.ball_radius * 2.1  # Slight gap between balls
        positions = [
            # Row 1 (tip) - 8-ball
            (0, 0),
            # Row 2
            (-ball_spacing, -ball_spacing),
            (ball_spacing, -ball_spacing),
            # Row 3
            (-ball_spacing * 2, -ball_spacing * 2),
            (0, -ball_spacing * 2),
            (ball_spacing * 2, -ball_spacing * 2),
            # Row 4
            (-ball_spacing * 3, -ball_spacing * 3),
            (-ball_spacing, -ball_spacing * 3),
            (ball_spacing, -ball_spacing * 3),
            (ball_spacing * 3, -ball_spacing * 3),
            # Row 5 (base)
            (-ball_spacing * 4, -ball_spacing * 4),
            (-ball_spacing * 2, -ball_spacing * 4),
            (0, -ball_spacing * 4),
            (ball_spacing * 2, -ball_spacing * 4),
            (ball_spacing * 4, -ball_spacing * 4),
        ]

        for i, (dx, dy) in enumerate(positions[:15]):  # 15 balls in triangle
            ball_id = i + 1
            if ball_id < 8:
                ball_type = "solid"
            elif ball_id > 8:
                ball_type = "stripe"
            else:
                ball_type = "eight"
            color = ball_colors[min(i, len(ball_colors) - 1)]

            balls.append(
                {
                    "id": ball_id,
                    "type": ball_type,
                    "color": color,
                    "x": rack_x + dx,
                    "y": rack_y + dy,
                    "active": True,
                }
            )

        return balls

    def _draw_table(self, frame):
        """Draw the pool table background"""
        # Table felt (green)
        cv2.rectangle(
            frame,
            (self.table_x, self.table_y),
            (self.table_x + self.table_width, self.table_y + self.table_height),
            (34, 139, 34),
            -1,
        )  # Forest green

        # Table rails (brown)
        rail_width = 20
        cv2.rectangle(
            frame,
            (self.table_x - rail_width, self.table_y - rail_width),
            (
                self.table_x + self.table_width + rail_width,
                self.table_y + self.table_height + rail_width,
            ),
            (101, 67, 33),
            -1,
        )  # Brown

        # Table felt (on top of rails)
        cv2.rectangle(
            frame,
            (self.table_x, self.table_y),
            (self.table_x + self.table_width, self.table_y + self.table_height),
            (34, 139, 34),
            -1,
        )  # Forest green

        # Pockets (simplified as black circles)
        pocket_radius = 25
        pocket_positions = [
            (self.table_x, self.table_y),  # top-left
            (self.table_x + self.table_width, self.table_y),  # top-right
            (self.table_x, self.table_y + self.table_height),  # bottom-left
            (
                self.table_x + self.table_width,
                self.table_y + self.table_height,
            ),  # bottom-right
            (self.table_x + self.table_width // 2, self.table_y),  # top-middle
            (
                self.table_x + self.table_width // 2,
                self.table_y + self.table_height,
            ),  # bottom-middle
        ]

        for px, py in pocket_positions:
            cv2.circle(frame, (px, py), pocket_radius, (0, 0, 0), -1)

    def _place_aruco_markers(self, frame):
        """Place ArUco markers at table corners with white background for contrast"""
        if not self.markers:
            return

        marker_offset = 50  # Reduced offset

        # Marker positions: 0=top-left, 1=top-right, 2=bottom-right, 3=bottom-left
        positions = [
            (self.table_x - marker_offset, self.table_y - marker_offset),  # 0: top-left
            (
                self.table_x + self.table_width - self.marker_size + marker_offset,
                self.table_y - marker_offset,
            ),  # 1: top-right
            (
                self.table_x + self.table_width - self.marker_size + marker_offset,
                self.table_y + self.table_height - self.marker_size + marker_offset,
            ),  # 2: bottom-right
            (
                self.table_x - marker_offset,
                self.table_y + self.table_height - self.marker_size + marker_offset,
            ),  # 3: bottom-left
        ]

        for marker_id, (x, y) in enumerate(positions):
            if marker_id not in self.markers or self.markers[marker_id] is None:
                continue

            # Check bounds and adjust if necessary
            x = max(0, min(x, frame.shape[1] - self.marker_size))
            y = max(0, min(y, frame.shape[0] - self.marker_size))

            # Add white background for contrast
            cv2.rectangle(
                frame,
                (x - 5, y - 5),
                (x + self.marker_size + 5, y + self.marker_size + 5),
                (255, 255, 255),
                -1,
            )

            marker_img = self.markers[marker_id]

            # Place marker on white background
            try:
                frame[y : y + self.marker_size, x : x + self.marker_size] = marker_img
            except Exception as e:
                print(f"Failed to place marker {marker_id} at ({x},{y}): {e}")

    def _draw_balls(self, frame):
        """Draw balls on the table"""
        for ball in self.balls:
            if not ball["active"]:
                continue

            x, y = int(ball["x"]), int(ball["y"])
            color = ball["color"]

            # Draw ball shadow
            cv2.circle(frame, (x + 2, y + 2), self.ball_radius, (0, 0, 0), -1)

            # Draw ball
            cv2.circle(frame, (x, y), self.ball_radius, color, -1)

            # Draw ball number
            if ball["id"] > 0:  # Don't number the cue ball
                text_color = (0, 0, 0) if sum(color) > 400 else (255, 255, 255)
                cv2.putText(
                    frame,
                    str(ball["id"]),
                    (x - 6, y + 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    text_color,
                    1,
                )

            # Draw stripe pattern for stripe balls
            if ball["type"] == "stripe" and ball["id"] > 8:
                cv2.circle(frame, (x, y), self.ball_radius - 3, (255, 255, 255), 2)

    def animate_balls(self, frame_count):
        """Animate ball positions for more realistic simulation"""
        # Simple animation - balls drift slightly
        for i, ball in enumerate(self.balls):
            if ball["id"] == 0:  # Move cue ball slightly
                ball["x"] += math.sin(frame_count * 0.02) * 0.5
                ball["y"] += math.cos(frame_count * 0.03) * 0.3
            else:
                # Other balls have subtle motion
                ball["x"] += math.sin(frame_count * 0.01 + i) * 0.2
                ball["y"] += math.cos(frame_count * 0.015 + i) * 0.1

    def pot_ball(self, ball_id):
        """Simulate potting a ball"""
        for ball in self.balls:
            if ball["id"] == ball_id:
                ball["active"] = False
                print(f"🎱 Ball {ball_id} potted!")
                break

    def reset_balls(self):
        """Reset all balls to initial positions"""
        self.balls = self._initialize_balls()
        print("🎱 Balls reset to initial position")

    def generate_frame(self, frame_count=0):
        """Generate a single synthetic frame"""
        # Create black background
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Draw table elements
        self._draw_table(frame)

        # Animate and draw balls
        self.animate_balls(frame_count)
        self._draw_balls(frame)

        # Place ArUco markers LAST (so they're not covered by noise)
        self._place_aruco_markers(frame)

        # Add title and debug info
        cv2.putText(
            frame,
            "PoolMind Virtual Table",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"Frame: {frame_count}",
            (10, self.height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (200, 200, 200),
            1,
        )

        # Add marker info for debugging
        active_markers = len([m for m in self.markers.values() if m is not None])
        cv2.putText(
            frame,
            f"ArUco Markers: {active_markers}/4",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            1,
        )
        cv2.putText(
            frame,
            f"Marker size: {self.marker_size}px",
            (10, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        return frame


def main():
    """Main demo function"""
    print("🎱 PoolMind Virtual Table Simulator")
    print("=" * 50)

    # Initialize virtual table
    virtual_table = VirtualPoolTable()

    # Interactive mode
    print("\n🎮 Controls:")
    print("  SPACE - Pot random ball")
    print("  R     - Reset all balls")
    print("  Q/ESC - Quit")
    print("  Any   - Continue")

    frame_count = 0

    try:
        while True:
            # Generate frame
            frame = virtual_table.generate_frame(frame_count)

            # Display frame
            cv2.imshow("Virtual Pool Table", frame)

            # Handle keyboard input
            key = cv2.waitKey(30) & 0xFF

            if key == ord("q") or key == 27:  # Q or ESC
                break
            elif key == ord(" "):  # SPACE - pot random ball
                active_balls = [
                    b for b in virtual_table.balls if b["active"] and b["id"] > 0
                ]
                if active_balls:
                    rng = np.random.default_rng(int(time.time()))
                    ball_to_pot = rng.choice(active_balls)
                    virtual_table.pot_ball(ball_to_pot["id"])
            elif key == ord("r"):  # R - reset
                virtual_table.reset_balls()
                frame_count = 0

            frame_count += 1

            # Auto-pot balls occasionally for demo
            if frame_count % 300 == 0:  # Every 10 seconds at 30fps
                active_balls = [
                    b for b in virtual_table.balls if b["active"] and b["id"] > 0
                ]
                if active_balls and len(active_balls) > 3:  # Keep some balls
                    rng = np.random.default_rng(int(time.time()) + frame_count)
                    ball_to_pot = rng.choice(active_balls)
                    virtual_table.pot_ball(ball_to_pot["id"])

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")

    finally:
        cv2.destroyAllWindows()
        print("🎯 Virtual table demo finished!")


if __name__ == "__main__":
    main()
