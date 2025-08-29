#!/usr/bin/env python3
"""
Replay System for PoolMind Physics Simulation
Records and replays ball movements and interactions
"""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import cv2
import numpy as np


class ReplaySystem:
    """
    System for recording and replaying simulation sequences
    """

    def __init__(self, replay_dir: str = "replays"):
        self.replay_dir = Path(replay_dir)
        self.replay_dir.mkdir(exist_ok=True)

        # Recording state
        self.is_recording = False
        self.current_recording = []
        self.recording_start_time = 0
        self.recording_name = ""

        # Playback state
        self.is_playing = False
        self.playback_data = []
        self.playback_index = 0
        self.playback_start_time = 0
        self.playback_speed = 1.0

        print(f"📹 Replay system initialized - Directory: {self.replay_dir}")

    def start_recording(self, name: str = None):
        """Start recording a new sequence"""
        if self.is_recording:
            self.stop_recording()

        self.is_recording = True
        self.current_recording = []
        self.recording_start_time = time.time()
        self.recording_name = name or f"recording_{int(self.recording_start_time)}"

        print(f"🔴 Started recording: {self.recording_name}")

    def stop_recording(self):
        """Stop current recording and save to file"""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.current_recording:
            filepath = self.replay_dir / f"{self.recording_name}.json"
            replay_data = {
                "name": self.recording_name,
                "duration": time.time() - self.recording_start_time,
                "frame_count": len(self.current_recording),
                "timestamp": self.recording_start_time,
                "frames": self.current_recording,
            }

            with open(filepath, "w") as f:
                json.dump(replay_data, f, indent=2)

            print(
                f"💾 Saved recording: {filepath} ({len(self.current_recording)} frames)"
            )
        else:
            print("⚠️  No frames recorded")

        self.current_recording = []

    def record_frame(self, balls: List[Any], events: List[Dict] = None):
        """Record current frame state"""
        if not self.is_recording:
            return

        frame_data = {
            "timestamp": time.time() - self.recording_start_time,
            "balls": [],
            "events": events or [],
        }

        # Record ball states
        for ball in balls:
            ball_data = {
                "id": ball.id,
                "x": ball.x,
                "y": ball.y,
                "vx": ball.vx,
                "vy": ball.vy,
                "active": ball.active,
                "type": ball.type,
                "color": ball.color,
            }
            frame_data["balls"].append(ball_data)

        self.current_recording.append(frame_data)

    def load_replay(self, filepath: str) -> bool:
        """Load a replay file"""
        try:
            with open(filepath, "r") as f:
                self.playback_data = json.load(f)

            self.playback_index = 0
            self.is_playing = False
            print(f"📂 Loaded replay: {filepath}")
            print(f"   Duration: {self.playback_data['duration']:.1f}s")
            print(f"   Frames: {self.playback_data['frame_count']}")
            return True

        except Exception as e:
            print(f"❌ Failed to load replay {filepath}: {e}")
            return False

    def start_playback(self, speed: float = 1.0):
        """Start playing back loaded replay"""
        if not self.playback_data:
            print("⚠️  No replay data loaded")
            return

        self.is_playing = True
        self.playback_index = 0
        self.playback_start_time = time.time()
        self.playback_speed = speed

        print(f"▶️  Started playback at {speed}x speed")

    def stop_playback(self):
        """Stop current playback"""
        self.is_playing = False
        self.playback_index = 0
        print("⏹️  Stopped playback")

    def update_playback(self, balls: List[Any]) -> bool:
        """Update balls from playback data"""
        if not self.is_playing or not self.playback_data:
            return False

        frames = self.playback_data["frames"]
        if self.playback_index >= len(frames):
            self.stop_playback()
            return False

        # Get current frame based on time
        elapsed_time = (time.time() - self.playback_start_time) * self.playback_speed
        target_frame = None

        for i, frame in enumerate(frames[self.playback_index :], self.playback_index):
            if frame["timestamp"] <= elapsed_time:
                target_frame = frame
                self.playback_index = i
            else:
                break

        if target_frame:
            # Apply frame data to balls
            for ball_data in target_frame["balls"]:
                ball = next((b for b in balls if b.id == ball_data["id"]), None)
                if ball:
                    ball.x = ball_data["x"]
                    ball.y = ball_data["y"]
                    ball.vx = ball_data["vx"]
                    ball.vy = ball_data["vy"]
                    ball.active = ball_data["active"]
            return True

        return False

    def get_replay_files(self) -> List[str]:
        """Get list of available replay files"""
        return [str(f) for f in self.replay_dir.glob("*.json")]

    def get_playback_progress(self) -> Tuple[float, str]:
        """Get current playback progress"""
        if not self.is_playing or not self.playback_data:
            return 0.0, "Not playing"

        total_duration = self.playback_data["duration"]
        elapsed = (time.time() - self.playback_start_time) * self.playback_speed
        progress = min(elapsed / total_duration, 1.0) if total_duration > 0 else 0.0

        status = f"{elapsed:.1f}s / {total_duration:.1f}s ({progress*100:.1f}%)"
        return progress, status


class AnalysisEngine:
    """
    Engine for analyzing recorded sequences and providing insights
    """

    def __init__(self):
        self.analysis_cache = {}

    def analyze_sequence(self, replay_data: Dict) -> Dict[str, Any]:
        """Analyze a replay sequence for insights"""
        if not replay_data or "frames" not in replay_data:
            return {}

        frames = replay_data["frames"]
        if not frames:
            return {}

        analysis = {
            "total_duration": replay_data.get("duration", 0),
            "total_frames": len(frames),
            "ball_statistics": self._analyze_ball_movement(frames),
            "collision_events": self._detect_collisions(frames),
            "pocket_events": self._detect_pockets(frames),
            "shot_analysis": self._analyze_shots(frames),
        }

        return analysis

    def _analyze_ball_movement(self, frames: List[Dict]) -> Dict[str, Any]:
        """Analyze ball movement patterns"""
        ball_stats = {}

        for frame in frames:
            for ball_data in frame["balls"]:
                ball_id = ball_data["id"]
                if ball_id not in ball_stats:
                    ball_stats[ball_id] = {
                        "total_distance": 0.0,
                        "max_speed": 0.0,
                        "avg_speed": 0.0,
                        "positions": [],
                        "active_time": 0.0,
                    }

                stats = ball_stats[ball_id]
                stats["positions"].append((ball_data["x"], ball_data["y"]))

                if ball_data["active"]:
                    stats["active_time"] += 1

                # Calculate speed
                speed = (ball_data["vx"] ** 2 + ball_data["vy"] ** 2) ** 0.5
                stats["max_speed"] = max(stats["max_speed"], speed)

        # Calculate distances and average speeds
        for ball_id, stats in ball_stats.items():
            positions = stats["positions"]
            total_distance = 0.0

            for i in range(1, len(positions)):
                dx = positions[i][0] - positions[i - 1][0]
                dy = positions[i][1] - positions[i - 1][1]
                total_distance += (dx**2 + dy**2) ** 0.5

            stats["total_distance"] = total_distance
            stats["avg_speed"] = total_distance / len(positions) if positions else 0.0

        return ball_stats

    def _detect_collisions(self, frames: List[Dict]) -> List[Dict]:
        """Detect collision events between balls"""
        collisions = []
        previous_positions = {}

        for frame_idx, frame in enumerate(frames):
            current_positions = {}

            for ball_data in frame["balls"]:
                if ball_data["active"]:
                    current_positions[ball_data["id"]] = (
                        ball_data["x"],
                        ball_data["y"],
                    )

            # Check for collisions (simplified - based on proximity)
            for ball1_id, pos1 in current_positions.items():
                for ball2_id, pos2 in current_positions.items():
                    if ball1_id >= ball2_id:
                        continue

                    distance = (
                        (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2
                    ) ** 0.5

                    if distance < 25:  # Collision threshold
                        collision = {
                            "frame": frame_idx,
                            "timestamp": frame["timestamp"],
                            "ball1": ball1_id,
                            "ball2": ball2_id,
                            "position": (
                                (pos1[0] + pos2[0]) / 2,
                                (pos1[1] + pos2[1]) / 2,
                            ),
                        }
                        collisions.append(collision)

            previous_positions = current_positions.copy()

        return collisions

    def _detect_pockets(self, frames: List[Dict]) -> List[Dict]:
        """Detect when balls are potted"""
        pocket_events = []
        previous_active = set()

        for frame_idx, frame in enumerate(frames):
            current_active = set()

            for ball_data in frame["balls"]:
                if ball_data["active"]:
                    current_active.add(ball_data["id"])

            # Check for newly inactive balls
            potted = previous_active - current_active
            for ball_id in potted:
                pocket_event = {
                    "frame": frame_idx,
                    "timestamp": frame["timestamp"],
                    "ball_id": ball_id,
                }
                pocket_events.append(pocket_event)

            previous_active = current_active.copy()

        return pocket_events

    def _analyze_shots(self, frames: List[Dict]) -> List[Dict]:
        """Analyze individual shots (cue ball movements)"""
        shots = []
        cue_ball_moving = False
        shot_start_frame = 0

        for frame_idx, frame in enumerate(frames):
            cue_ball = next((b for b in frame["balls"] if b["id"] == 0), None)
            if not cue_ball:
                continue

            speed = (cue_ball["vx"] ** 2 + cue_ball["vy"] ** 2) ** 0.5
            is_moving = speed > 0.1

            if is_moving and not cue_ball_moving:
                # Shot started
                cue_ball_moving = True
                shot_start_frame = frame_idx

            elif not is_moving and cue_ball_moving:
                # Shot ended
                cue_ball_moving = False
                shot = {
                    "start_frame": shot_start_frame,
                    "end_frame": frame_idx,
                    "duration": frame["timestamp"]
                    - frames[shot_start_frame]["timestamp"],
                }
                shots.append(shot)

        return shots

    def generate_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a text report from analysis"""
        if not analysis:
            return "No analysis data available"

        report = "📊 SEQUENCE ANALYSIS REPORT\n"
        report += "=" * 50 + "\n\n"

        # Basic info
        report += f"Duration: {analysis['total_duration']:.1f} seconds\n"
        report += f"Total Frames: {analysis['total_frames']}\n\n"

        # Ball statistics
        ball_stats = analysis.get("ball_statistics", {})
        if ball_stats:
            report += "🎱 BALL MOVEMENT STATISTICS\n"
            report += "-" * 30 + "\n"

            for ball_id, stats in ball_stats.items():
                report += f"Ball {ball_id}:\n"
                report += f"  Distance: {stats['total_distance']:.1f}px\n"
                report += f"  Max Speed: {stats['max_speed']:.1f}px/frame\n"
                report += f"  Avg Speed: {stats['avg_speed']:.1f}px/frame\n"
                report += f"  Active Time: {stats['active_time']} frames\n\n"

        # Collisions
        collisions = analysis.get("collision_events", [])
        if collisions:
            report += f"💥 COLLISIONS ({len(collisions)} detected)\n"
            report += "-" * 30 + "\n"
            for collision in collisions[:5]:  # Show first 5
                report += f"Frame {collision['frame']}: Ball {collision['ball1']} ↔ Ball {collision['ball2']}\n"
            if len(collisions) > 5:
                report += f"... and {len(collisions) - 5} more\n"
            report += "\n"

        # Pockets
        pockets = analysis.get("pocket_events", [])
        if pockets:
            report += f"🎯 POTTED BALLS ({len(pockets)} balls)\n"
            report += "-" * 30 + "\n"
            for pocket in pockets:
                report += f"Frame {pocket['frame']}: Ball {pocket['ball_id']} potted\n"
            report += "\n"

        # Shots
        shots = analysis.get("shot_analysis", [])
        if shots:
            report += f"🏹 SHOTS ANALYSIS ({len(shots)} shots)\n"
            report += "-" * 30 + "\n"
            for i, shot in enumerate(shots[:3]):  # Show first 3
                report += f"Shot {i+1}: Duration {shot['duration']:.1f}s (frames {shot['start_frame']}-{shot['end_frame']})\n"
            if len(shots) > 3:
                report += f"... and {len(shots) - 3} more shots\n"

        return report


def main():
    """Demo of replay system"""
    print("📹 PoolMind Replay System Demo")
    print("=" * 40)

    replay_system = ReplaySystem()
    analysis_engine = AnalysisEngine()

    # List available replays
    replay_files = replay_system.get_replay_files()
    print(f"Found {len(replay_files)} replay files:")
    for i, filepath in enumerate(replay_files):
        print(f"  {i+1}. {Path(filepath).name}")

    if replay_files:
        # Load and analyze first replay
        if replay_system.load_replay(replay_files[0]):
            analysis = analysis_engine.analyze_sequence(replay_system.playback_data)
            report = analysis_engine.generate_report(analysis)
            print("\n" + report)
    else:
        print("No replay files found. Record some sequences first!")


if __name__ == "__main__":
    main()
