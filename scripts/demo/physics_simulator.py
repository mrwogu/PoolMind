#!/usr/bin/env python3
"""
Advanced Physics-Based Pool Table Simulator for PoolMind
Implements realistic ball physics, collisions, and game mechanics
"""
import math
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import yaml


class Ball:
    """
    Physics-enabled pool ball with velocity, collision detection, and realistic movement
    """

    def __init__(
        self,
        ball_id: int,
        x: float,
        y: float,
        ball_type: str = "solid",
        color: Tuple[int, int, int] = (255, 255, 255),
        radius: float = 12.0,
    ):
        # Identity
        self.id = ball_id
        self.type = ball_type
        self.color = color
        self.radius = radius
        self.active = True

        # Physics state
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0  # velocity x
        self.vy = 0.0  # velocity y
        self.mass = 1.0  # normalized mass

        # Physics constants
        self.friction = 0.98  # friction coefficient (energy loss per frame)
        self.min_velocity = 0.1  # minimum velocity before stopping

    def update_physics(self, dt: float = 1.0):
        """Update ball position based on velocity and apply friction"""
        if not self.active:
            return

        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Apply friction
        self.vx *= self.friction
        self.vy *= self.friction

        # Stop if velocity is too small
        if abs(self.vx) < self.min_velocity and abs(self.vy) < self.min_velocity:
            self.vx = 0.0
            self.vy = 0.0

    def apply_impulse(self, impulse_x: float, impulse_y: float):
        """Apply an impulse (instant velocity change) to the ball"""
        self.vx += impulse_x / self.mass
        self.vy += impulse_y / self.mass

    def get_speed(self) -> float:
        """Get current speed (magnitude of velocity)"""
        return math.sqrt(self.vx**2 + self.vy**2)

    def is_moving(self) -> bool:
        """Check if ball is currently moving"""
        return self.get_speed() > self.min_velocity

    def get_position(self) -> Tuple[float, float]:
        """Get current position as tuple"""
        return (self.x, self.y)

    def distance_to(self, other: "Ball") -> float:
        """Calculate distance to another ball"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx**2 + dy**2)

    def is_colliding_with(self, other: "Ball") -> bool:
        """Check if this ball is colliding with another ball"""
        if not self.active or not other.active or self.id == other.id:
            return False
        return self.distance_to(other) <= (self.radius + other.radius)


class PhysicsEngine:
    """
    Physics engine for ball collisions, wall bounces, and realistic movement
    """

    def __init__(self, table_bounds: Tuple[float, float, float, float]):
        # Table boundaries: (x_min, y_min, x_max, y_max)
        (
            self.table_x_min,
            self.table_y_min,
            self.table_x_max,
            self.table_y_max,
        ) = table_bounds

        # Physics constants
        self.restitution = 0.8  # energy preserved in collisions (0-1)
        self.wall_restitution = 0.7  # energy preserved in wall bounces

        # Pockets configuration
        self.pocket_radius = 25.0
        self.pocket_positions = [
            (self.table_x_min, self.table_y_min),  # top-left
            (self.table_x_max, self.table_y_min),  # top-right
            (self.table_x_min, self.table_y_max),  # bottom-left
            (self.table_x_max, self.table_y_max),  # bottom-right
            ((self.table_x_min + self.table_x_max) / 2, self.table_y_min),  # top-mid
            ((self.table_x_min + self.table_x_max) / 2, self.table_y_max),  # bottom-mid
        ]

    def update_balls(self, balls: List[Ball], dt: float = 1.0):
        """Update all balls physics including collisions"""
        # Update individual ball physics
        for ball in balls:
            if ball.active:
                ball.update_physics(dt)

        # Handle collisions between balls
        self._handle_ball_collisions(balls)

        # Handle wall collisions
        for ball in balls:
            if ball.active:
                self._handle_wall_collision(ball)

        # Check for balls falling into pockets
        self._check_pocket_collisions(balls)

    def _handle_ball_collisions(self, balls: List[Ball]):
        """Handle elastic collisions between balls"""
        for i, ball1 in enumerate(balls):
            if not ball1.active:
                continue

            for j, ball2 in enumerate(balls[i + 1 :], i + 1):
                if not ball2.active:
                    continue

                if ball1.is_colliding_with(ball2):
                    self._resolve_ball_collision(ball1, ball2)

    def _resolve_ball_collision(self, ball1: Ball, ball2: Ball):
        """Resolve collision between two balls using elastic collision physics"""
        # Calculate collision normal
        dx = ball2.x - ball1.x
        dy = ball2.y - ball1.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return  # Avoid division by zero

        # Normalize collision vector
        nx = dx / distance
        ny = dy / distance

        # Separate balls to prevent overlap
        overlap = (ball1.radius + ball2.radius) - distance
        if overlap > 0:
            separation = overlap / 2
            ball1.x -= nx * separation
            ball1.y -= ny * separation
            ball2.x += nx * separation
            ball2.y += ny * separation

        # Calculate relative velocity
        dvx = ball1.vx - ball2.vx
        dvy = ball1.vy - ball2.vy

        # Calculate relative velocity along collision normal
        dvn = dvx * nx + dvy * ny

        # Objects separating, no collision
        if dvn > 0:
            return

        # Calculate collision impulse
        impulse = 2 * dvn / (ball1.mass + ball2.mass) * self.restitution

        # Apply impulse to balls
        ball1.vx -= impulse * ball2.mass * nx
        ball1.vy -= impulse * ball2.mass * ny
        ball2.vx += impulse * ball1.mass * nx
        ball2.vy += impulse * ball1.mass * ny

    def _handle_wall_collision(self, ball: Ball):
        """Handle collision with table walls"""
        # Left wall
        if ball.x - ball.radius <= self.table_x_min:
            ball.x = self.table_x_min + ball.radius
            ball.vx = -ball.vx * self.wall_restitution

        # Right wall
        elif ball.x + ball.radius >= self.table_x_max:
            ball.x = self.table_x_max - ball.radius
            ball.vx = -ball.vx * self.wall_restitution

        # Top wall
        if ball.y - ball.radius <= self.table_y_min:
            ball.y = self.table_y_min + ball.radius
            ball.vy = -ball.vy * self.wall_restitution

        # Bottom wall
        elif ball.y + ball.radius >= self.table_y_max:
            ball.y = self.table_y_max - ball.radius
            ball.vy = -ball.vy * self.wall_restitution

    def _check_pocket_collisions(self, balls: List[Ball]):
        """Check if any balls have fallen into pockets"""
        for ball in balls:
            if not ball.active:
                continue

            for pocket_x, pocket_y in self.pocket_positions:
                distance_to_pocket = math.sqrt(
                    (ball.x - pocket_x) ** 2 + (ball.y - pocket_y) ** 2
                )

                if distance_to_pocket <= self.pocket_radius:
                    # Ball is close to pocket, apply "sucking" effect
                    if distance_to_pocket <= ball.radius:
                        # Ball has fallen into pocket
                        ball.active = False
                        print(f"🎱 Ball {ball.id} potted!")
                    else:
                        # Apply attraction force towards pocket
                        force_strength = 0.5
                        dx = pocket_x - ball.x
                        dy = pocket_y - ball.y
                        ball.vx += dx * force_strength / distance_to_pocket
                        ball.vy += dy * force_strength / distance_to_pocket

    def apply_cue_strike(
        self, cue_ball: Ball, target_x: float, target_y: float, force: float
    ):
        """Apply a cue strike to the cue ball"""
        if not cue_ball.active:
            return

        # Calculate direction from cue ball to target
        dx = target_x - cue_ball.x
        dy = target_y - cue_ball.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return

        # Normalize direction and apply force
        nx = dx / distance
        ny = dy / distance

        # Apply impulse to cue ball
        cue_ball.apply_impulse(nx * force, ny * force)


class AdvancedVirtualTable:
    """
    Advanced virtual pool table with physics simulation
    """

    def __init__(self, config_path="config/config.yaml"):
        # Load configuration
        with open(config_path, "r") as f:
            self.cfg = yaml.safe_load(f)

        # Camera settings
        self.width = self.cfg["camera"]["width"]
        self.height = self.cfg["camera"]["height"]

        # Table dimensions
        self.table_margin = 100
        self.table_width = self.width - (2 * self.table_margin)
        self.table_height = int(self.table_width * 0.5)
        self.table_x = self.table_margin
        self.table_y = (self.height - self.table_height) // 2

        # Initialize physics engine
        table_bounds = (
            self.table_x,
            self.table_y,
            self.table_x + self.table_width,
            self.table_y + self.table_height,
        )
        self.physics = PhysicsEngine(table_bounds)

        # Ball configuration
        self.ball_radius = 12.0

        # Initialize ArUco markers
        try:
            self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
            self.markers = self._generate_aruco_markers()
            print("   ArUco markers: Generated successfully")
        except Exception as e:
            print(f"   ArUco markers: Failed to generate ({e})")
            self.markers = {}

        # Initialize balls with physics
        self.balls = self._initialize_physics_balls()

        # Interaction state
        self.mouse_pos = (0, 0)
        self.aiming = False
        self.cue_ball = self._get_cue_ball()

        print("🎱 Advanced Virtual Table initialized:")
        print(f"   Frame size: {self.width}x{self.height}")
        print(f"   Table area: {self.table_width}x{self.table_height}")
        print(f"   Physics: Enabled with {len(self.balls)} balls")

    def _generate_aruco_markers(self):
        """Generate ArUco marker images"""
        markers = {}
        marker_size = 120

        for marker_id in [0, 1, 2, 3]:
            try:
                marker_img = cv2.aruco.generateImageMarker(
                    self.aruco_dict, marker_id, marker_size
                )
                marker_bgr = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
                markers[marker_id] = marker_bgr
            except Exception as e:
                print(f"Failed to generate marker {marker_id}: {e}")
                markers[marker_id] = None
        return markers

    def _initialize_physics_balls(self) -> List[Ball]:
        """Initialize balls with physics properties"""
        balls = []

        # Cue ball (white) - left side
        cue_x = self.table_x + self.table_width // 4
        cue_y = self.table_y + self.table_height // 2
        balls.append(
            Ball(
                ball_id=0,
                x=cue_x,
                y=cue_y,
                ball_type="cue",
                color=(255, 255, 255),
                radius=self.ball_radius,
            )
        )

        # Object balls in triangle formation
        rack_x = self.table_x + 3 * self.table_width // 4
        rack_y = self.table_y + self.table_height // 2

        ball_colors = [
            (0, 255, 255),  # 1 - yellow
            (0, 0, 255),  # 2 - red
            (255, 0, 0),  # 3 - blue
            (128, 0, 128),  # 4 - purple
            (255, 165, 0),  # 5 - orange
            (0, 128, 0),  # 6 - green
            (128, 0, 0),  # 7 - maroon
            (0, 0, 0),  # 8 - black
            (255, 255, 0),  # 9 - yellow stripe
            (255, 0, 255),  # 10 - red stripe
            (255, 255, 255),  # 11 - blue stripe
            (200, 100, 200),  # 12 - purple stripe
            (255, 200, 100),  # 13 - orange stripe
            (100, 255, 100),  # 14 - green stripe
            (200, 100, 100),  # 15 - maroon stripe
        ]

        # Proper triangle formation
        ball_spacing = self.ball_radius * 2.05  # Tight formation
        positions = [
            # Row 1
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
            # Row 5
            (-ball_spacing * 4, -ball_spacing * 4),
            (-ball_spacing * 2, -ball_spacing * 4),
            (0, -ball_spacing * 4),
            (ball_spacing * 2, -ball_spacing * 4),
            (ball_spacing * 4, -ball_spacing * 4),
        ]

        for i, (dx, dy) in enumerate(positions[:15]):
            ball_id = i + 1
            if ball_id < 8:
                ball_type = "solid"
            elif ball_id > 8:
                ball_type = "stripe"
            else:
                ball_type = "eight"
            color = ball_colors[min(i, len(ball_colors) - 1)]

            balls.append(
                Ball(
                    ball_id=ball_id,
                    x=rack_x + dx,
                    y=rack_y + dy,
                    ball_type=ball_type,
                    color=color,
                    radius=self.ball_radius,
                )
            )

        return balls

    def _get_cue_ball(self) -> Optional[Ball]:
        """Get the cue ball (ID 0)"""
        for ball in self.balls:
            if ball.id == 0:
                return ball
        return None

    def update_physics(self, dt: float = 1.0):
        """Update physics simulation"""
        self.physics.update_balls(self.balls, dt)

    def handle_mouse_callback(self, event, x, y, _flags, _param):
        """Handle mouse events for cue aiming"""
        self.mouse_pos = (x, y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.aiming = True
        elif event == cv2.EVENT_LBUTTONUP and self.aiming:
            self.aiming = False
            # Apply cue strike
            if self.cue_ball and self.cue_ball.active:
                # Calculate force based on distance
                dx = x - self.cue_ball.x
                dy = y - self.cue_ball.y
                distance = math.sqrt(dx**2 + dy**2)
                force = min(distance / 50.0, 10.0)  # Limit maximum force

                self.physics.apply_cue_strike(self.cue_ball, x, y, force)

    def _draw_table(self, frame):
        """Draw the pool table"""
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
        )

        # Table felt (green)
        cv2.rectangle(
            frame,
            (self.table_x, self.table_y),
            (self.table_x + self.table_width, self.table_y + self.table_height),
            (34, 139, 34),
            -1,
        )

        # Draw pockets
        for pocket_x, pocket_y in self.physics.pocket_positions:
            cv2.circle(
                frame,
                (int(pocket_x), int(pocket_y)),
                int(self.physics.pocket_radius),
                (0, 0, 0),
                -1,
            )

    def _place_aruco_markers(self, frame):
        """Place ArUco markers at corners"""
        if not self.markers:
            return

        marker_size = 120
        marker_offset = 50

        positions = [
            (self.table_x - marker_offset, self.table_y - marker_offset),
            (
                self.table_x + self.table_width - marker_size + marker_offset,
                self.table_y - marker_offset,
            ),
            (
                self.table_x + self.table_width - marker_size + marker_offset,
                self.table_y + self.table_height - marker_size + marker_offset,
            ),
            (
                self.table_x - marker_offset,
                self.table_y + self.table_height - marker_size + marker_offset,
            ),
        ]

        for marker_id, (x, y) in enumerate(positions):
            if marker_id not in self.markers or self.markers[marker_id] is None:
                continue

            x = max(0, min(x, frame.shape[1] - marker_size))
            y = max(0, min(y, frame.shape[0] - marker_size))

            # White background
            cv2.rectangle(
                frame,
                (x - 5, y - 5),
                (x + marker_size + 5, y + marker_size + 5),
                (255, 255, 255),
                -1,
            )

            try:
                frame[y : y + marker_size, x : x + marker_size] = self.markers[
                    marker_id
                ]
            except Exception as e:
                print(f"Failed to place marker {marker_id}: {e}")

    def _draw_balls(self, frame):
        """Draw balls with physics state"""
        for ball in self.balls:
            if not ball.active:
                continue

            x, y = int(ball.x), int(ball.y)

            # Draw shadow
            cv2.circle(frame, (x + 2, y + 2), int(ball.radius), (0, 0, 0), -1)

            # Draw ball
            cv2.circle(frame, (x, y), int(ball.radius), ball.color, -1)

            # Draw velocity vector for moving balls
            if ball.is_moving():
                end_x = int(x + ball.vx * 5)
                end_y = int(y + ball.vy * 5)
                cv2.arrowedLine(frame, (x, y), (end_x, end_y), (255, 255, 255), 2)

            # Draw ball number
            if ball.id > 0:
                text_color = (0, 0, 0) if sum(ball.color) > 400 else (255, 255, 255)
                cv2.putText(
                    frame,
                    str(ball.id),
                    (x - 6, y + 4),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    text_color,
                    1,
                )

            # Stripe pattern for stripe balls
            if ball.type == "stripe" and ball.id > 8:
                cv2.circle(frame, (x, y), int(ball.radius) - 3, (255, 255, 255), 2)

    def _draw_aiming_line(self, frame):
        """Draw aiming line when player is aiming"""
        if self.aiming and self.cue_ball and self.cue_ball.active:
            start_x, start_y = int(self.cue_ball.x), int(self.cue_ball.y)
            end_x, end_y = self.mouse_pos

            # Draw aiming line
            cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 255), 2)

            # Draw force indicator
            dx = end_x - start_x
            dy = end_y - start_y
            distance = math.sqrt(dx**2 + dy**2)
            force = min(distance / 50.0, 10.0)

            # Force bar
            bar_width = int(force * 20)
            cv2.rectangle(frame, (10, 50), (10 + bar_width, 70), (0, 255, 255), -1)
            cv2.rectangle(frame, (10, 50), (210, 70), (255, 255, 255), 2)

            cv2.putText(
                frame,
                f"Force: {force:.1f}",
                (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

    def generate_frame(self, frame_count=0):
        """Generate frame with physics simulation"""
        # Create frame
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Draw table elements
        self._draw_table(frame)
        self._place_aruco_markers(frame)
        self._draw_balls(frame)
        self._draw_aiming_line(frame)

        # Physics info
        moving_balls = sum(1 for ball in self.balls if ball.is_moving())
        active_balls = sum(1 for ball in self.balls if ball.active)

        cv2.putText(
            frame,
            "PoolMind Advanced Physics Simulator",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Active: {active_balls}/16  Moving: {moving_balls}  Frame: {frame_count}",
            (10, self.height - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        # Controls info
        controls = [
            "Controls:",
            "Left Click + Drag: Aim cue",
            "R: Reset balls",
            "1-5: Set force presets",
            "SPACE: Random strike",
            "Q/ESC: Quit",
        ]

        for i, text in enumerate(controls):
            color = (0, 255, 255) if i == 0 else (200, 200, 200)
            cv2.putText(
                frame,
                text,
                (self.width - 200, 30 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                color,
                1,
            )

        return frame

    def reset_balls(self):
        """Reset all balls to initial positions"""
        self.balls = self._initialize_physics_balls()
        self.cue_ball = self._get_cue_ball()
        print("🎱 Balls reset with physics enabled")

    def apply_random_strike(self):
        """Apply a random strike for demo purposes"""
        if self.cue_ball and self.cue_ball.active:
            import random

            angle = random.uniform(0, 2 * math.pi)
            force = random.uniform(3, 8)
            target_x = self.cue_ball.x + math.cos(angle) * 100
            target_y = self.cue_ball.y + math.sin(angle) * 100
            self.physics.apply_cue_strike(self.cue_ball, target_x, target_y, force)


def main():
    """Main demo function"""
    WINDOW_NAME = "Advanced Physics Simulator"

    print("🎱 PoolMind Advanced Physics Simulator")
    print("=" * 50)

    # Initialize simulator
    simulator = AdvancedVirtualTable()

    # Set up mouse callback
    cv2.namedWindow(WINDOW_NAME)
    # pylint: disable=no-member
    cv2.setMouseCallback(WINDOW_NAME, simulator.handle_mouse_callback)

    frame_count = 0
    last_time = time.time()
    fps_counter = []

    try:
        while True:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time

            # Update physics
            simulator.update_physics(dt)

            # Generate and display frame
            frame = simulator.generate_frame(frame_count)
            cv2.imshow(WINDOW_NAME, frame)

            # Calculate FPS
            fps_counter.append(current_time)
            fps_counter = [t for t in fps_counter if current_time - t < 1.0]
            fps = len(fps_counter)

            # Handle input
            key = cv2.waitKey(16) & 0xFF  # ~60 FPS

            if key == ord("q") or key == 27:  # Q or ESC
                break
            elif key == ord("r"):  # Reset
                simulator.reset_balls()
                frame_count = 0
            elif key == ord(" "):  # Random strike
                simulator.apply_random_strike()
            elif key >= ord("1") and key <= ord("5"):  # Force presets
                if simulator.cue_ball and simulator.cue_ball.active:
                    force = (key - ord("0")) * 2
                    simulator.physics.apply_cue_strike(
                        simulator.cue_ball,
                        simulator.cue_ball.x + 100,
                        simulator.cue_ball.y,
                        force,
                    )

            frame_count += 1

            # Show FPS in title
            if frame_count % 30 == 0:
                cv2.setWindowTitle(WINDOW_NAME, f"Physics Simulator - FPS: {fps}")

    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")

    finally:
        cv2.destroyAllWindows()
        print("🎯 Advanced physics simulator finished!")


if __name__ == "__main__":
    main()
