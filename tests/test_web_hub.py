"""
Tests for PoolMind Web Hub functionality
"""
import threading
import time
from unittest.mock import Mock, patch

import cv2
import numpy as np
import pytest

from poolmind.web.hub import FrameHub


class TestFrameHub:
    """Test cases for FrameHub class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.hub = FrameHub(max_events=10)

    def test_hub_initialization(self):
        """Test hub initializes correctly"""
        assert self.hub.frame_bgr is None
        assert self.hub.state == {}
        assert len(self.hub.events) == 0
        assert self.hub.events.maxlen == 10

    def test_update_frame_with_state(self):
        """Test updating frame with state"""
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        test_state = {"active_balls": 5, "game_state": "playing"}

        self.hub.update_frame(test_frame, test_state)

        assert self.hub.frame_bgr is not None
        assert np.array_equal(self.hub.frame_bgr, test_frame)
        assert self.hub.state == test_state

    def test_update_frame_without_state(self):
        """Test updating frame without state"""
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)

        self.hub.update_frame(test_frame)

        assert self.hub.frame_bgr is not None
        assert np.array_equal(self.hub.frame_bgr, test_frame)
        assert self.hub.state == {}

    def test_push_event(self):
        """Test pushing events"""
        event1 = {"type": "ball_potted", "ball_id": 5}
        event2 = {"type": "game_start"}

        self.hub.push_event(event1)
        self.hub.push_event(event2)

        assert len(self.hub.events) == 2
        assert self.hub.events[0]["type"] == "ball_potted"
        assert self.hub.events[1]["type"] == "game_start"
        assert "ts" in self.hub.events[0]
        assert "ts" in self.hub.events[1]

    def test_event_queue_maxlen(self):
        """Test event queue respects maxlen"""
        # Add more events than maxlen
        for i in range(15):
            self.hub.push_event({"type": f"event_{i}"})

        assert len(self.hub.events) == 10
        # Should have the last 10 events
        assert self.hub.events[-1]["type"] == "event_14"
        assert self.hub.events[0]["type"] == "event_5"

    @patch("cv2.imencode")
    def test_get_jpeg_success(self, mock_imencode):
        """Test successful JPEG encoding"""
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imencode.return_value = (True, np.array([1, 2, 3, 4]))

        self.hub.update_frame(test_frame)
        jpeg_data = self.hub.get_jpeg(quality=75)

        assert jpeg_data == bytes([1, 2, 3, 4])
        mock_imencode.assert_called_once_with(
            ".jpg", test_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        )

    @patch("cv2.imencode")
    def test_get_jpeg_failure(self, mock_imencode):
        """Test JPEG encoding failure"""
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_imencode.return_value = (False, None)

        self.hub.update_frame(test_frame)
        jpeg_data = self.hub.get_jpeg()

        assert jpeg_data is None

    def test_get_jpeg_no_frame(self):
        """Test get_jpeg when no frame is available"""
        jpeg_data = self.hub.get_jpeg()
        assert jpeg_data is None

    def test_snapshot(self):
        """Test snapshot functionality"""
        test_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        test_state = {"active_balls": 3}
        test_event = {"type": "test_event"}

        self.hub.update_frame(test_frame, test_state)
        self.hub.push_event(test_event)

        frame_copy, state_copy, events_copy = self.hub.snapshot()

        # Verify copies are independent
        assert frame_copy is not None
        assert np.array_equal(frame_copy, test_frame)
        assert frame_copy is not self.hub.frame_bgr
        assert state_copy == test_state
        assert state_copy is not self.hub.state
        assert len(events_copy) == 1
        assert events_copy[0]["type"] == "test_event"

    def test_snapshot_no_frame(self):
        """Test snapshot when no frame is available"""
        test_state = {"active_balls": 0}
        self.hub.state = test_state

        frame_copy, state_copy, events_copy = self.hub.snapshot()

        assert frame_copy is None
        assert state_copy == test_state
        assert events_copy == []

    def test_thread_safety(self):
        """Test thread safety of hub operations"""
        results = []

        def update_worker():
            for i in range(100):
                frame = np.full((10, 10, 3), i, dtype=np.uint8)
                state = {"counter": i}
                self.hub.update_frame(frame, state)
                time.sleep(0.001)

        def read_worker():
            for _ in range(100):
                snapshot = self.hub.snapshot()
                results.append(snapshot)
                time.sleep(0.001)

        # Start threads
        update_thread = threading.Thread(target=update_worker)
        read_thread = threading.Thread(target=read_worker)

        update_thread.start()
        read_thread.start()

        update_thread.join()
        read_thread.join()

        # Verify no exceptions occurred and we got results
        assert len(results) > 0
        # All snapshots should be valid (frame can be None during initialization)
        for frame, state, events in results:
            assert isinstance(state, dict)
            assert isinstance(events, list)

    def test_custom_maxlen(self):
        """Test hub with custom maxlen"""
        hub = FrameHub(max_events=3)

        for i in range(5):
            hub.push_event({"type": f"event_{i}"})

        assert len(hub.events) == 3
        assert hub.events[0]["type"] == "event_2"
        assert hub.events[-1]["type"] == "event_4"
