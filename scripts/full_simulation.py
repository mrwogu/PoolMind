#!/usr/bin/env python3
"""
PoolMind Full Pipeline Demo with Virtual Table
Integrates virtual table simulator with the complete PoolMind computer vision pipeline
"""
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import yaml

# Add src to Python path for imports
sys.path.insert(0, "src")
sys.path.insert(0, "scripts")

from virtual_table import VirtualPoolTable

from poolmind.calib.markers import MarkerHomography
from poolmind.detect.balls import BallDetector
from poolmind.game.engine import GameEngine
from poolmind.table.geometry import TableGeometry
from poolmind.track.tracker import CentroidTracker
from poolmind.ui.overlay import Overlay
from poolmind.web.hub import FrameHub


class PoolMindSimulation:
    """
    Complete PoolMind simulation using virtual table
    """

    def __init__(self, config_path="config/config.yaml"):
        print("🎱 Initializing PoolMind Full Pipeline Simulation...")

        # Load configuration
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

        # Initialize components
        self.virtual_table = VirtualPoolTable(config_path)
        self.calibration = MarkerHomography(self.cfg.get("calibration", {}))
        self.detector = BallDetector(self.cfg.get("detection", {}))
        self.tracker = CentroidTracker(self.cfg.get("tracking", {}))

        # Table geometry
        table_cfg = self.cfg.get("calibration", {})
        self.table = TableGeometry(table_cfg)

        # Game engine
        game_cfg = self.cfg.get("game", {})
        self.engine = GameEngine(self.table, game_cfg)

        # UI overlay
        ui_cfg = self.cfg.get("ui", {})
        self.overlay = Overlay(ui_cfg, self.table)

        # Web interface - simplified without web server for now
        self.hub = FrameHub() if self.cfg.get("web", {}).get("enabled", False) else None

        # Stats
        self.frame_count = 0
        self.fps_counter = []
        self.last_time = time.time()

        print("✅ All components initialized successfully!")

    def start_web_server(self):
        """Start web server in background thread - disabled for simulation"""
        print("🌐 Web server disabled in simulation mode")

    def process_frame(self, frame):
        """Process a single frame through the complete pipeline"""
        processed_frame = frame.copy()

        # Step 1: ArUco marker detection and homography
        (
            homography_matrix,
            h_inv,
            debug_markers,
        ) = self.calibration.homography_from_frame(frame)

        # Step 2: Perspective transformation
        warped = None
        if homography_matrix is not None:
            warped = self.table.warp(frame, homography_matrix)

        # Step 3: Ball detection
        detections = []
        if warped is not None:
            detections = self.detector.detect(warped)

        # Step 4: Object tracking
        tracks = self.tracker.update(detections)

        # Step 5: Game engine update
        self.engine.update(tracks)
        game_state = self.engine.get_state()
        game_events = self.engine.consume_events()

        # Step 6: Calculate FPS
        current_time = time.time()
        self.fps_counter.append(current_time)
        self.fps_counter = [t for t in self.fps_counter if current_time - t < 1.0]
        fps = len(self.fps_counter)

        # Step 7: Draw overlay
        processed_frame = self.overlay.draw(
            frame_bgr=processed_frame,
            warped_bgr=warped,
            H_inv=h_inv,
            tracks=tracks,
            fps=fps,
            dbg_markers=debug_markers,
        )

        # Step 8: Add simulation info
        self._draw_simulation_info(processed_frame, game_state, game_events)

        # Step 9: Update web interface
        if self.hub:
            self.hub.update_frame(processed_frame, game_state)
            for event in game_events:
                self.hub.push_event(event)

        return processed_frame, game_state, game_events

    def _draw_simulation_info(self, frame, game_state, game_events):
        """Draw simulation-specific information"""
        h, w = frame.shape[:2]

        # Title
        cv2.putText(
            frame,
            "PoolMind Full Pipeline Demo",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )

        # Pipeline status
        y_offset = 60
        pipeline_steps = [
            "1. Virtual Table Generation",
            "2. ArUco Marker Detection",
            "3. Homography Transformation",
            "4. Ball Detection (HoughCircles)",
            "5. Centroid Tracking",
            "6. Game Engine Processing",
            "7. UI Overlay Rendering",
        ]

        for i, step in enumerate(pipeline_steps):
            color = (0, 255, 0)  # Green for active steps
            cv2.putText(
                frame,
                step,
                (10, y_offset + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color,
                1,
            )

        # Game state info
        state_text = [
            f"Active Balls: {game_state.get('active_balls', 0)}",
            f"Potted: {game_state.get('potted', 0)}",
            f"Game State: {game_state.get('game_state', 'unknown')}",
            f"Current Player: {game_state.get('current_player', 1)}",
        ]

        for i, text in enumerate(state_text):
            cv2.putText(
                frame,
                text,
                (w - 300, 30 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
            )

        # Recent events
        if game_events:
            cv2.putText(
                frame,
                "Recent Events:",
                (w - 300, 150),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 255),
                1,
            )
            for i, event in enumerate(game_events[-3:]):  # Show last 3 events
                event_text = f"{event.get('type', 'unknown')}"
                cv2.putText(
                    frame,
                    event_text,
                    (w - 300, 175 + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 0, 255),
                    1,
                )

        # Controls
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

    def run_simulation(self):
        """Run the complete simulation"""
        print("🚀 Starting PoolMind simulation...")
        print("🎮 Controls: SPACE=pot ball, R=reset, Q=quit")

        if self.hub:
            print("🌐 Web interface available at: http://localhost:8000")

        try:
            while True:
                # Generate virtual table frame
                virtual_frame = self.virtual_table.generate_frame(self.frame_count)

                # Process through PoolMind pipeline
                processed_frame, _, _ = self.process_frame(virtual_frame)

                # Display result
                cv2.imshow("PoolMind Full Pipeline Demo", processed_frame)

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
                    # Reset tracker manually since it doesn't have reset method
                    self.tracker = CentroidTracker(self.cfg.get("tracking", {}))
                    self.frame_count = 0

                self.frame_count += 1

                # Auto-demo: pot balls occasionally
                if self.frame_count % 400 == 0:  # Every ~13 seconds
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
            print("\n🛑 Simulation interrupted by user")

        finally:
            cv2.destroyAllWindows()
            print("🎯 PoolMind simulation finished!")


def main():
    """Main function"""
    print("🎱 PoolMind Full Pipeline Simulation")
    print("=" * 50)

    # Check if config exists
    config_path = "config/config.yaml"
    if not Path(config_path).exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("Please run from the PoolMind root directory")
        return

    # Run simulation
    simulation = PoolMindSimulation(config_path)
    simulation.run_simulation()


if __name__ == "__main__":
    main()
