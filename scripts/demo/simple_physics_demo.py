#!/usr/bin/env python3
"""
PoolMind Simple Physics Demo
Simplified version for easy testing and demonstration
"""
import math
import time

import cv2
import numpy as np
import yaml


class SimpleBall:
    """Simple ball with basic physics"""

    def __init__(self, ball_id, x, y, color=(255, 255, 255), radius=12):
        self.id = ball_id
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.color = color
        self.radius = radius
        self.active = True
        self.friction = 0.98
        self.min_velocity = 0.1

    def update(self):
        """Update ball position and apply friction"""
        if not self.active:
            return

        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction

        if abs(self.vx) < self.min_velocity and abs(self.vy) < self.min_velocity:
            self.vx = 0.0
            self.vy = 0.0

    def is_moving(self):
        """Check if ball is moving"""
        return abs(self.vx) > self.min_velocity or abs(self.vy) > self.min_velocity

    def distance_to(self, other):
        """Distance to another ball"""
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def apply_force(self, fx, fy):
        """Apply force to ball"""
        self.vx += fx
        self.vy += fy


class SimplePhysicsDemo:
    """Simple physics demonstration"""

    def __init__(self):
        # Screen setup
        self.width = 1280
        self.height = 720

        # Table setup
        self.table_margin = 100
        self.table_x = self.table_margin
        self.table_y = 100
        self.table_width = self.width - 2 * self.table_margin
        self.table_height = 400

        # Physics constants
        self.ball_radius = 12
        self.restitution = 0.8
        self.wall_restitution = 0.7

        # Initialize balls
        self.balls = self._create_balls()
        self.cue_ball = self.balls[0]

        # Interaction
        self.mouse_pos = (0, 0)
        self.aiming = False

        print("🎱 Simple Physics Demo Initialized")
        print(f"   Table: {self.table_width}x{self.table_height}")
        print(f"   Balls: {len(self.balls)}")

    def _create_balls(self):
        """Create initial ball setup"""
        balls = []

        # Cue ball (white)
        cue_x = self.table_x + self.table_width // 4
        cue_y = self.table_y + self.table_height // 2
        balls.append(SimpleBall(0, cue_x, cue_y, (255, 255, 255), self.ball_radius))

        # Some target balls
        colors = [
            (0, 255, 255),  # yellow
            (0, 0, 255),  # red
            (255, 0, 0),  # blue
            (128, 0, 128),  # purple
            (255, 165, 0),  # orange
            (0, 128, 0),  # green
            (0, 0, 0),  # black
        ]

        # Place balls in formation
        start_x = self.table_x + 3 * self.table_width // 4
        start_y = self.table_y + self.table_height // 2
        spacing = self.ball_radius * 2.2

        for i, color in enumerate(colors):
            row = i // 3
            col = i % 3
            x = start_x + col * spacing
            y = start_y + (row - 1) * spacing
            balls.append(SimpleBall(i + 1, x, y, color, self.ball_radius))

        return balls

    def handle_collisions(self):
        """Handle ball-to-ball collisions"""
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball1 = self.balls[i]
                ball2 = self.balls[j]

                if not ball1.active or not ball2.active:
                    continue

                distance = ball1.distance_to(ball2)
                min_distance = ball1.radius + ball2.radius

                if distance < min_distance:
                    # Collision detected
                    self._resolve_collision(ball1, ball2, distance, min_distance)

    def _resolve_collision(self, ball1, ball2, distance, min_distance):
        """Resolve collision between two balls"""
        if distance == 0:
            return

        # Collision normal
        nx = (ball2.x - ball1.x) / distance
        ny = (ball2.y - ball1.y) / distance

        # Separate balls
        overlap = min_distance - distance
        separation = overlap / 2
        ball1.x -= nx * separation
        ball1.y -= ny * separation
        ball2.x += nx * separation
        ball2.y += ny * separation

        # Relative velocity
        dvx = ball1.vx - ball2.vx
        dvy = ball1.vy - ball2.vy
        dvn = dvx * nx + dvy * ny

        if dvn > 0:
            return  # Objects separating

        # Apply collision response
        impulse = 2 * dvn / 2 * self.restitution  # Assuming equal mass
        ball1.vx -= impulse * nx
        ball1.vy -= impulse * ny
        ball2.vx += impulse * nx
        ball2.vy += impulse * ny

    def handle_walls(self):
        """Handle wall collisions"""
        for ball in self.balls:
            if not ball.active:
                continue

            # Left wall
            if ball.x - ball.radius <= self.table_x:
                ball.x = self.table_x + ball.radius
                ball.vx = -ball.vx * self.wall_restitution

            # Right wall
            elif ball.x + ball.radius >= self.table_x + self.table_width:
                ball.x = self.table_x + self.table_width - ball.radius
                ball.vx = -ball.vx * self.wall_restitution

            # Top wall
            if ball.y - ball.radius <= self.table_y:
                ball.y = self.table_y + ball.radius
                ball.vy = -ball.vy * self.wall_restitution

            # Bottom wall
            elif ball.y + ball.radius >= self.table_y + self.table_height:
                ball.y = self.table_y + self.table_height - ball.radius
                ball.vy = -ball.vy * self.wall_restitution

    def update_physics(self):
        """Update all physics"""
        # Update ball positions
        for ball in self.balls:
            ball.update()

        # Handle collisions
        self.handle_collisions()
        self.handle_walls()

    def handle_mouse(self, event, x, y, flags, param):
        """Handle mouse events"""
        self.mouse_pos = (x, y)

        if event == cv2.EVENT_LBUTTONDOWN:
            self.aiming = True
        elif event == cv2.EVENT_LBUTTONUP and self.aiming:
            self.aiming = False
            self._apply_cue_strike(x, y)

    def _apply_cue_strike(self, target_x, target_y):
        """Apply cue strike to cue ball"""
        if not self.cue_ball.active:
            return

        dx = target_x - self.cue_ball.x
        dy = target_y - self.cue_ball.y
        distance = math.sqrt(dx * dx + dy * dy)

        if distance == 0:
            return

        # Normalize and scale force
        force = min(distance / 100.0, 8.0)
        fx = (dx / distance) * force
        fy = (dy / distance) * force

        self.cue_ball.apply_force(fx, fy)

    def draw_table(self, frame):
        """Draw the pool table"""
        # Table rails
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

        # Table felt
        cv2.rectangle(
            frame,
            (self.table_x, self.table_y),
            (self.table_x + self.table_width, self.table_y + self.table_height),
            (34, 139, 34),
            -1,
        )

    def draw_balls(self, frame):
        """Draw all balls"""
        for ball in self.balls:
            if not ball.active:
                continue

            x, y = int(ball.x), int(ball.y)

            # Draw shadow
            cv2.circle(frame, (x + 2, y + 2), ball.radius, (0, 0, 0), -1)

            # Draw ball
            cv2.circle(frame, (x, y), ball.radius, ball.color, -1)

            # Draw velocity vector for moving balls
            if ball.is_moving():
                end_x = int(x + ball.vx * 10)
                end_y = int(y + ball.vy * 10)
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

    def draw_aiming(self, frame):
        """Draw aiming line"""
        if self.aiming and self.cue_ball.active:
            start_x, start_y = int(self.cue_ball.x), int(self.cue_ball.y)
            end_x, end_y = self.mouse_pos

            # Draw aim line
            cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 255), 2)

            # Force indicator
            dx = end_x - start_x
            dy = end_y - start_y
            distance = math.sqrt(dx * dx + dy * dy)
            force = min(distance / 100.0, 8.0)

            # Force bar
            bar_width = int(force * 30)
            cv2.rectangle(frame, (10, 50), (10 + bar_width, 70), (0, 255, 255), -1)
            cv2.rectangle(frame, (10, 50), (250, 70), (255, 255, 255), 2)
            cv2.putText(
                frame,
                f"Force: {force:.1f}",
                (10, 45),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

    def draw_info(self, frame, frame_count):
        """Draw information"""
        # Title
        cv2.putText(
            frame,
            "PoolMind Simple Physics Demo",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        # Stats
        moving_balls = sum(1 for ball in self.balls if ball.is_moving())
        active_balls = sum(1 for ball in self.balls if ball.active)

        info = [
            f"Active: {active_balls}/{len(self.balls)}",
            f"Moving: {moving_balls}",
            f"Frame: {frame_count}",
        ]

        for i, text in enumerate(info):
            cv2.putText(
                frame,
                text,
                (10, self.height - 80 + i * 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (200, 200, 200),
                1,
            )

        # Controls
        controls = [
            "Controls:",
            "Click+Drag: Aim and shoot",
            "1-5: Force presets",
            "SPACE: Random shot",
            "R: Reset balls",
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

    def generate_frame(self, frame_count):
        """Generate complete frame"""
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        self.draw_table(frame)
        self.draw_balls(frame)
        self.draw_aiming(frame)
        self.draw_info(frame, frame_count)

        return frame

    def reset_balls(self):
        """Reset all balls to initial positions"""
        self.balls = self._create_balls()
        self.cue_ball = self.balls[0]
        print("🎱 Balls reset")

    def apply_random_shot(self):
        """Apply random shot for demo"""
        if self.cue_ball.active:
            import random

            angle = random.uniform(0, 2 * math.pi)
            force = random.uniform(2, 6)
            fx = math.cos(angle) * force
            fy = math.sin(angle) * force
            self.cue_ball.apply_force(fx, fy)

    def run(self):
        """Main demo loop"""
        window_name = "Simple Physics Demo"
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self.handle_mouse)

        frame_count = 0

        print("\n🎮 Simple Physics Demo Started!")
        print("Click and drag to aim, release to shoot!")

        try:
            while True:
                # Update physics
                self.update_physics()

                # Generate and show frame
                frame = self.generate_frame(frame_count)
                cv2.imshow(window_name, frame)

                # Handle input
                key = cv2.waitKey(16) & 0xFF

                if key == ord("q") or key == 27:  # Q or ESC
                    break
                elif key == ord("r"):  # Reset
                    self.reset_balls()
                    frame_count = 0
                elif key == ord(" "):  # Random shot
                    self.apply_random_shot()
                elif key >= ord("1") and key <= ord("5"):  # Force presets
                    if self.cue_ball.active:
                        force = (key - ord("0")) * 1.5
                        self.cue_ball.apply_force(force, 0)

                frame_count += 1

        except KeyboardInterrupt:
            print("\n🛑 Demo interrupted")
        finally:
            cv2.destroyAllWindows()
            print("🎯 Simple demo finished!")


def main():
    """Main function"""
    print("🎱 PoolMind Simple Physics Demo")
    print("=" * 40)

    demo = SimplePhysicsDemo()
    demo.run()


if __name__ == "__main__":
    main()
