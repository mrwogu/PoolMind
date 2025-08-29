#!/usr/bin/env python3
"""
Enhanced PoolMind Simulation with Advanced Physics
Integrates physics-based simulation with the complete PoolMind pipeline
"""
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
import yaml

# Add src to Python path for imports
sys.path.insert(0, "src")
sys.path.insert(0, "scripts/demo")

from physics_simulator import AdvancedVirtualTable, Ball

from poolmind.calib.markers import MarkerHomography
from poolmind.detect.balls import BallDetector
from poolmind.game.engine import GameEngine
from poolmind.table.geometry import TableGeometry
from poolmind.track.tracker import CentroidTracker
from poolmind.ui.overlay import Overlay
from poolmind.web.hub import FrameHub


class ScenarioManager:
    """
    Manages different simulation scenarios for training and testing
    """

    def __init__(self, virtual_table: AdvancedVirtualTable):
        self.virtual_table = virtual_table
        self.scenarios = {
            "standard_break": self._setup_standard_break,
            "scattered_balls": self._setup_scattered_balls,
            "corner_pocket": self._setup_corner_pocket,
            "bank_shot": self._setup_bank_shot,
            "combination_shot": self._setup_combination_shot,
            "defense_position": self._setup_defense_position,
            "end_game": self._setup_end_game,
        }
        self.current_scenario = "standard_break"

    def apply_scenario(self, scenario_name: str):
        """Apply a specific scenario setup"""
        if scenario_name in self.scenarios:
            self.current_scenario = scenario_name
            self.scenarios[scenario_name]()
            print(f"🎬 Applied scenario: {scenario_name}")
        else:
            print(f"❌ Unknown scenario: {scenario_name}")

    def _setup_standard_break(self):
        """Standard 8-ball break formation"""
        self.virtual_table.reset_balls()

    def _setup_scattered_balls(self):
        """Balls scattered across the table"""
        import random

        self.virtual_table.reset_balls()

        # Scatter balls randomly but avoid overlaps
        for ball in self.virtual_table.balls[1:]:  # Skip cue ball
            if ball.active:
                attempts = 0
                while attempts < 100:
                    new_x = random.uniform(
                        self.virtual_table.table_x + ball.radius * 2,
                        self.virtual_table.table_x
                        + self.virtual_table.table_width
                        - ball.radius * 2,
                    )
                    new_y = random.uniform(
                        self.virtual_table.table_y + ball.radius * 2,
                        self.virtual_table.table_y
                        + self.virtual_table.table_height
                        - ball.radius * 2,
                    )

                    # Check for overlaps
                    overlap = False
                    for other_ball in self.virtual_table.balls:
                        if other_ball.id != ball.id and other_ball.active:
                            dx = new_x - other_ball.x
                            dy = new_y - other_ball.y
                            distance = (dx**2 + dy**2) ** 0.5
                            if distance < (ball.radius + other_ball.radius) * 1.2:
                                overlap = True
                                break

                    if not overlap:
                        ball.x = new_x
                        ball.y = new_y
                        break

                    attempts += 1

    def _setup_corner_pocket(self):
        """Setup for practicing corner pocket shots"""
        self.virtual_table.reset_balls()

        # Position cue ball in center
        cue_ball = self.virtual_table.cue_ball
        if cue_ball:
            cue_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width // 2
            )
            cue_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height // 2
            )

        # Position target ball near corner pocket
        if len(self.virtual_table.balls) > 1:
            target_ball = self.virtual_table.balls[1]
            target_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width * 0.8
            )
            target_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height * 0.2
            )

        # Deactivate other balls except a few
        for ball in self.virtual_table.balls[2:10]:
            ball.active = False

    def _setup_bank_shot(self):
        """Setup for practicing bank shots"""
        self.virtual_table.reset_balls()

        # Position cue ball
        cue_ball = self.virtual_table.cue_ball
        if cue_ball:
            cue_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width * 0.3
            )
            cue_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height * 0.7
            )

        # Position target ball on opposite side
        if len(self.virtual_table.balls) > 1:
            target_ball = self.virtual_table.balls[1]
            target_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width * 0.8
            )
            target_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height * 0.3
            )

        # Deactivate most other balls
        for ball in self.virtual_table.balls[2:]:
            ball.active = False

    def _setup_combination_shot(self):
        """Setup for practicing combination shots"""
        self.virtual_table.reset_balls()

        # Position cue ball
        cue_ball = self.virtual_table.cue_ball
        if cue_ball:
            cue_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width * 0.25
            )
            cue_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height * 0.5
            )

        # Position balls in line for combination
        if len(self.virtual_table.balls) > 2:
            ball1 = self.virtual_table.balls[1]
            ball2 = self.virtual_table.balls[2]

            ball1.x = self.virtual_table.table_x + self.virtual_table.table_width * 0.5
            ball1.y = self.virtual_table.table_y + self.virtual_table.table_height * 0.5

            ball2.x = self.virtual_table.table_x + self.virtual_table.table_width * 0.6
            ball2.y = self.virtual_table.table_y + self.virtual_table.table_height * 0.5

        # Deactivate other balls
        for ball in self.virtual_table.balls[3:]:
            ball.active = False

    def _setup_defense_position(self):
        """Setup defensive position scenario"""
        self.virtual_table.reset_balls()

        # Cluster some balls together
        cluster_x = self.virtual_table.table_x + self.virtual_table.table_width * 0.7
        cluster_y = self.virtual_table.table_y + self.virtual_table.table_height * 0.3

        for i, ball in enumerate(self.virtual_table.balls[1:5]):
            ball.x = cluster_x + (i % 2) * ball.radius * 2.1
            ball.y = cluster_y + (i // 2) * ball.radius * 2.1

        # Position cue ball for difficult shot
        cue_ball = self.virtual_table.cue_ball
        if cue_ball:
            cue_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width * 0.2
            )
            cue_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height * 0.8
            )

    def _setup_end_game(self):
        """End game scenario with few balls left"""
        self.virtual_table.reset_balls()

        # Keep only 8-ball, cue ball, and one other
        for ball in self.virtual_table.balls:
            if ball.id not in [0, 1, 8]:  # Keep cue, ball 1, and 8-ball
                ball.active = False

        # Position 8-ball near pocket
        eight_ball = next((b for b in self.virtual_table.balls if b.id == 8), None)
        if eight_ball:
            eight_ball.x = (
                self.virtual_table.table_x + self.virtual_table.table_width * 0.85
            )
            eight_ball.y = (
                self.virtual_table.table_y + self.virtual_table.table_height * 0.15
            )

    def get_scenario_list(self) -> List[str]:
        """Get list of available scenarios"""
        return list(self.scenarios.keys())

    def next_scenario(self):
        """Switch to next scenario"""
        scenarios = self.get_scenario_list()
        current_index = scenarios.index(self.current_scenario)
        next_index = (current_index + 1) % len(scenarios)
        self.apply_scenario(scenarios[next_index])

    def previous_scenario(self):
        """Switch to previous scenario"""
        scenarios = self.get_scenario_list()
        current_index = scenarios.index(self.current_scenario)
        prev_index = (current_index - 1) % len(scenarios)
        self.apply_scenario(scenarios[prev_index])


class EnhancedPoolMindSimulation:
    """
    Enhanced PoolMind simulation with physics and multiple scenarios
    """

    def __init__(self, config_path="config/config.yaml"):
        print("🎱 Initializing Enhanced PoolMind Simulation...")

        # Load configuration
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

        # Initialize physics-based virtual table
        self.virtual_table = AdvancedVirtualTable(config_path)

        # Initialize scenario manager
        self.scenario_manager = ScenarioManager(self.virtual_table)

        # Initialize PoolMind components
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

        # Web interface hub
        self.hub = FrameHub() if self.cfg.get("web", {}).get("enabled", False) else None

        # Simulation state
        self.frame_count = 0
        self.fps_counter = []
        self.last_time = time.time()
        self.paused = False
        self.show_debug = True

        print("✅ Enhanced simulation initialized successfully!")

    def process_frame(self, frame):
        """Process frame through complete PoolMind pipeline"""
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
        if self.show_debug:
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
        """Draw enhanced simulation information"""
        h, w = frame.shape[:2]

        # Title
        cv2.putText(
            frame,
            "Enhanced PoolMind Physics Simulation",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        # Current scenario
        cv2.putText(
            frame,
            f"Scenario: {self.scenario_manager.current_scenario}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 0),
            1,
        )

        # Physics stats
        moving_balls = sum(1 for ball in self.virtual_table.balls if ball.is_moving())
        active_balls = sum(1 for ball in self.virtual_table.balls if ball.active)

        physics_info = [
            f"Active Balls: {active_balls}/16",
            f"Moving: {moving_balls}",
            f"Frame: {self.frame_count}",
            f"Paused: {'Yes' if self.paused else 'No'}",
        ]

        for i, text in enumerate(physics_info):
            cv2.putText(
                frame,
                text,
                (10, 90 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (200, 200, 200),
                1,
            )

        # Game state (right side)
        state_info = [
            f"Game State: {game_state.get('game_state', 'unknown')}",
            f"Current Player: {game_state.get('current_player', 1)}",
            f"Potted: {game_state.get('potted', 0)}",
        ]

        for i, text in enumerate(state_info):
            cv2.putText(
                frame,
                text,
                (w - 300, 30 + i * 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 0),
                1,
            )

        # Controls (right side, bottom)
        controls = [
            "Controls:",
            "SPACE: Pause/Resume",
            "N: Next scenario",
            "P: Previous scenario",
            "R: Reset balls",
            "1-5: Force presets",
            "D: Toggle debug",
            "Click+Drag: Aim cue",
            "Q/ESC: Quit",
        ]

        for i, text in enumerate(controls):
            color = (0, 255, 255) if i == 0 else (200, 200, 200)
            cv2.putText(
                frame,
                text,
                (w - 200, h - 200 + i * 18),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                color,
                1,
            )

        # Recent events
        if game_events:
            cv2.putText(
                frame,
                "Recent Events:",
                (w - 300, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 255),
                1,
            )
            for i, event in enumerate(game_events[-3:]):
                event_text = f"• {event.get('type', 'unknown')}"
                cv2.putText(
                    frame,
                    event_text,
                    (w - 300, 145 + i * 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 200, 200),
                    1,
                )

    def handle_input(self, key):
        """Handle keyboard input"""
        if key == ord(" "):  # Pause/Resume
            self.paused = not self.paused
            print(f"🎮 Simulation {'paused' if self.paused else 'resumed'}")
        elif key == ord("n"):  # Next scenario
            self.scenario_manager.next_scenario()
        elif key == ord("p"):  # Previous scenario
            self.scenario_manager.previous_scenario()
        elif key == ord("r"):  # Reset
            self.scenario_manager.apply_scenario(self.scenario_manager.current_scenario)
            self.frame_count = 0
        elif key == ord("d"):  # Toggle debug
            self.show_debug = not self.show_debug
            print(f"🔍 Debug overlay {'enabled' if self.show_debug else 'disabled'}")
        elif key >= ord("1") and key <= ord("5"):  # Force presets
            if self.virtual_table.cue_ball and self.virtual_table.cue_ball.active:
                force = (key - ord("0")) * 2
                self.virtual_table.physics.apply_cue_strike(
                    self.virtual_table.cue_ball,
                    self.virtual_table.cue_ball.x + 100,
                    self.virtual_table.cue_ball.y,
                    force,
                )

    def run(self):
        """Main simulation loop"""
        WINDOW_NAME = "Enhanced PoolMind Simulation"
        cv2.namedWindow(WINDOW_NAME)
        # pylint: disable=no-member
        cv2.setMouseCallback(WINDOW_NAME, self.virtual_table.handle_mouse_callback)

        print("\n🎮 Enhanced PoolMind Simulation Started!")
        print("=" * 50)

        try:
            while True:
                current_time = time.time()
                dt = current_time - self.last_time
                self.last_time = current_time

                # Update physics (only if not paused)
                if not self.paused:
                    self.virtual_table.update_physics(dt)

                # Generate virtual frame
                virtual_frame = self.virtual_table.generate_frame(self.frame_count)

                # Process through PoolMind pipeline
                processed_frame, _game_state, _game_events = self.process_frame(
                    virtual_frame
                )

                # Display result
                cv2.imshow(WINDOW_NAME, processed_frame)

                # Handle input
                key = cv2.waitKey(16) & 0xFF  # ~60 FPS

                if key == ord("q") or key == 27:  # Q or ESC
                    break
                elif key != 255:  # Any other key
                    self.handle_input(key)

                if not self.paused:
                    self.frame_count += 1

                # Update window title with FPS
                if self.frame_count % 30 == 0:
                    fps = len(self.fps_counter)
                    cv2.setWindowTitle(
                        WINDOW_NAME,
                        f"Enhanced Simulation - FPS: {fps} - {self.scenario_manager.current_scenario}",
                    )

        except KeyboardInterrupt:
            print("\n🛑 Simulation interrupted by user")

        finally:
            cv2.destroyAllWindows()
            print("🎯 Enhanced simulation finished!")


def main():
    """Main function"""
    print("🎱 PoolMind Enhanced Physics Simulation")
    print("=" * 50)

    simulation = EnhancedPoolMindSimulation()
    simulation.run()


if __name__ == "__main__":
    main()
