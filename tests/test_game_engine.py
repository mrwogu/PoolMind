"""
Tests for PoolMind game engine functionality
"""
from unittest.mock import Mock

import pytest

from poolmind.game.engine import GameEngine
from poolmind.table.geometry import TableGeometry


class TestGameEngine:
    """Test cases for GameEngine class"""

    def setup_method(self):
        """Set up test fixtures"""
        # Mock table geometry
        self.table = Mock(spec=TableGeometry)
        self.table.default_pockets.return_value = [
            (50, 50, 20),  # pocket at (50,50) with radius 20
            (200, 50, 20),  # pocket at (200,50) with radius 20
        ]

        self.config = {
            "disappear_for_pot": 6,
            "pocket_radius": 36,
            "enable_8ball_rules": False,
        }
        self.engine = GameEngine(self.table, self.config)

    def test_engine_initialization(self):
        """Test engine initializes with correct parameters"""
        assert self.engine.max_disappeared_for_pot == 6
        assert self.engine.pocket_radius == 36
        assert len(self.engine.track_history) == 0
        assert len(self.engine.disappear_counts) == 0
        assert len(self.engine.potted_ids) == 0
        assert len(self.engine.events) == 0

    def test_engine_with_default_config(self):
        """Test engine works with minimal config"""
        engine = GameEngine(self.table)
        assert engine.max_disappeared_for_pot == 6  # default
        assert engine.pocket_radius == 36  # default

    def test_update_with_new_tracks(self):
        """Test updating with new track data"""
        tracks = {1: (100, 100, 10, "cue"), 2: (150, 150, 10, "solid")}

        self.engine.update(tracks)

        # Check track history was updated
        assert 1 in self.engine.track_history
        assert 2 in self.engine.track_history
        assert self.engine.track_history[1] == [(100, 100)]
        assert self.engine.track_history[2] == [(150, 150)]

        # Check ball types were recorded
        assert self.engine.ball_types[1] == "cue"
        assert self.engine.ball_types[2] == "solid"

    def test_update_with_old_format_tracks(self):
        """Test updating with old format track data (x, y, r only)"""
        tracks = {1: (100, 100, 10), 2: (150, 150, 10)}

        self.engine.update(tracks)

        # Should still work but without color info
        assert 1 in self.engine.track_history
        assert 2 in self.engine.track_history

    def test_track_disappearance(self):
        """Test tracking ball disappearance"""
        # First update with tracks
        self.engine.update({1: (100, 100, 10, "cue")})

        # Second update without tracks
        self.engine.update({})

        # Ball should be marked as disappeared
        assert self.engine.disappear_counts[1] == 1

    def test_ball_potting_detection(self):
        """Test ball potting when near pocket"""
        # Add ball near pocket
        tracks = {1: (55, 55, 10, "solid")}  # Near pocket at (50, 50)
        self.engine.update(tracks)

        # Make ball disappear (simulate potting)
        for _ in range(self.engine.max_disappeared_for_pot + 1):
            self.engine.update({})

        # Ball should be marked as potted
        assert 1 in self.engine.potted_ids
        assert self.engine.score["potted"] == 1
        assert self.engine.score["solid_potted"] == 1

    def test_ball_potting_away_from_pocket(self):
        """Test ball not potted when far from pocket"""
        # Add ball far from any pocket
        tracks = {1: (300, 300, 10, "solid")}
        self.engine.update(tracks)

        # Make ball disappear
        for _ in range(self.engine.max_disappeared_for_pot + 1):
            self.engine.update({})

        # Ball should NOT be marked as potted
        assert 1 not in self.engine.potted_ids

    def test_get_state(self):
        """Test getting current game state"""
        # Add some tracks
        self.engine.update(
            {
                1: (100, 100, 10, "cue"),
                2: (150, 150, 10, "solid"),
                3: (200, 200, 10, "stripe"),
            }
        )

        state = self.engine.get_state()

        assert state["total_tracked"] == 3
        assert state["active_balls"] == 3
        assert state["active_cue"] == 1
        assert state["active_solid"] == 1
        assert state["active_stripe"] == 1
        assert state["potted"] == 0

    def test_get_state_with_potted_balls(self):
        """Test state after some balls are potted"""
        # Add ball near pocket and pot it
        self.engine.update({1: (55, 55, 10, "solid")})

        # Pot the ball
        for _ in range(self.engine.max_disappeared_for_pot + 1):
            self.engine.update({})

        state = self.engine.get_state()

        assert state["potted"] == 1
        assert state["solid_potted"] == 1
        assert state["active_balls"] == 0

    def test_reset_game(self):
        """Test game reset functionality"""
        # Add some game state
        self.engine.update({1: (100, 100, 10, "cue")})
        self.engine.potted_ids.add(2)
        self.engine.score["potted"] = 5
        self.engine.events.append({"type": "test", "info": "test event"})

        # Reset game
        self.engine.reset_game()

        # Core game state should be cleared
        assert len(self.engine.potted_ids) == 0
        assert self.engine.score["potted"] == 0
        assert not self.engine.shot_in_progress
        assert len(self.engine.last_shot_potted) == 0

        # Should have reset event
        events = self.engine.consume_events()
        assert len(events) >= 1
        assert any(e["type"] == "game_reset" for e in events)

    def test_consume_events(self):
        """Test consuming game events"""
        # Add some events
        self.engine.events = [
            {"type": "pot", "info": "ball potted"},
            {"type": "scratch", "info": "cue ball potted"},
        ]

        events = self.engine.consume_events()

        assert len(events) == 2
        assert events[0]["type"] == "pot"
        assert events[1]["type"] == "scratch"

        # Events should be cleared after consuming
        assert len(self.engine.events) == 0

    def test_track_history_limiting(self):
        """Test track history is limited to prevent memory issues"""
        tracks = {1: (100, 100, 10, "cue")}

        # Update many times
        for i in range(150):
            tracks[1] = (100 + i, 100, 10, "cue")
            self.engine.update(tracks)

        # History should be limited to 120 entries
        assert len(self.engine.track_history[1]) == 120

    def test_cue_ball_scratch_detection(self):
        """Test special handling for cue ball potting (scratch)"""
        # Add cue ball near pocket
        tracks = {1: (55, 55, 10, "cue")}
        self.engine.update(tracks)

        # Pot the cue ball
        for _ in range(self.engine.max_disappeared_for_pot + 1):
            self.engine.update({})

        # Should generate both pot and scratch events
        events = [e for e in self.engine.events if e["type"] in ["pot", "scratch"]]
        assert len(events) >= 1  # At least one event should be generated

        # Check score tracking
        assert self.engine.score["cue_potted"] >= 1

    def test_multiple_ball_types_scoring(self):
        """Test scoring different types of balls"""
        # Pot different types of balls
        ball_configs = [
            (55, 55, 10, "cue"),
            (55, 56, 10, "solid"),
            (55, 57, 10, "stripe"),
        ]

        for i, config in enumerate(ball_configs, 1):
            self.engine.update({i: config})
            # Pot each ball
            for _ in range(self.engine.max_disappeared_for_pot + 1):
                self.engine.update({})

        # Check individual scores
        assert self.engine.score["cue_potted"] >= 1
        assert self.engine.score["solid_potted"] >= 1
        assert self.engine.score["stripe_potted"] >= 1
