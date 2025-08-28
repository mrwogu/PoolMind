"""
Tests for PoolMind tracking functionality
"""
import numpy as np
import pytest

from poolmind.track.tracker import CentroidTracker


class TestCentroidTracker:
    """Test cases for CentroidTracker class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = {"max_disappeared": 8, "max_distance": 40}
        self.tracker = CentroidTracker(self.config)

    def test_tracker_initialization(self):
        """Test tracker initializes with correct parameters"""
        assert self.tracker.nextObjectID == 1
        assert self.tracker.maxDisappeared == 8
        assert self.tracker.maxDistance == 40
        assert len(self.tracker.objects) == 0
        assert len(self.tracker.disappeared) == 0

    def test_tracker_with_default_config(self):
        """Test tracker works with empty config (default values)"""
        tracker = CentroidTracker({})
        assert tracker.maxDisappeared == 8  # default value
        assert tracker.maxDistance == 40  # default value

    def test_update_first_detection(self):
        """Test updating with first detection creates new objects"""
        detections = [(50, 50, 10), (100, 100, 12)]

        result = self.tracker.update(detections)

        assert len(result) == 2
        assert 1 in result
        assert 2 in result
        assert result[1] == (50, 50, 10, "unknown")
        assert result[2] == (100, 100, 12, "unknown")

    def test_update_with_color_detection(self):
        """Test updating with color detection"""
        detections = [(50, 50, 10, "cue"), (100, 100, 12, "solid")]

        result = self.tracker.update(detections)

        assert len(result) == 2
        assert result[1] == (50, 50, 10, "cue")
        assert result[2] == (100, 100, 12, "solid")

    def test_update_no_detections(self):
        """Test updating with no detections"""
        # First add some objects
        self.tracker.update([(50, 50, 10)])

        # Then update with no detections
        result = self.tracker.update([])

        # Objects should still exist but marked as disappeared
        assert 1 in self.tracker.disappeared
        assert self.tracker.disappeared[1] == 1

    def test_object_disappearance_and_removal(self):
        """Test objects are removed after max disappeared frames"""
        # Add object
        self.tracker.update([(50, 50, 10)])

        # Update with no detections for max_disappeared + 1 times
        for _ in range(self.tracker.maxDisappeared + 1):
            self.tracker.update([])

        # Object should be removed
        assert len(self.tracker.objects) == 0
        assert len(self.tracker.disappeared) == 0

    def test_object_tracking_continuity(self):
        """Test objects maintain IDs when tracked continuously"""
        # First detection
        result1 = self.tracker.update([(50, 50, 10)])
        obj_id = list(result1.keys())[0]

        # Move object slightly
        result2 = self.tracker.update([(52, 52, 10)])

        # Should have same ID
        assert obj_id in result2
        assert result2[obj_id] == (52, 52, 10, "unknown")

    def test_object_association_by_distance(self):
        """Test objects are associated by closest distance"""
        # Add two objects
        self.tracker.update([(50, 50, 10), (100, 100, 10)])

        # Move them (within max distance)
        result = self.tracker.update([(55, 55, 10), (105, 105, 10)])

        # Should maintain same associations
        assert len(result) == 2
        # Objects should exist at new positions
        positions = [(obj[0], obj[1]) for obj in result.values()]
        assert (55, 55) in positions
        assert (105, 105) in positions

    def test_max_distance_threshold(self):
        """Test objects beyond max distance create new IDs"""
        # Add object
        self.tracker.update([(50, 50, 10)])

        # Move beyond max distance
        far_distance = self.tracker.maxDistance + 10
        result = self.tracker.update([(50 + far_distance, 50, 10)])

        # Old object should disappear, new object should be created
        # But old object won't be deleted until max_disappeared frames
        assert len(result) == 2  # old object still exists but disappeared

        # Verify new object has new ID
        object_ids = list(result.keys())
        assert 1 in object_ids  # original object
        assert 2 in object_ids  # new object

        # Original object should be marked as disappeared
        assert self.tracker.disappeared[1] == 1
        assert self.tracker.disappeared[2] == 0

    def test_distance_matrix_calculation(self):
        """Test distance matrix calculation"""
        A = np.array([[0, 0], [10, 10]])
        B = np.array([[0, 0], [5, 5]])

        distances = self.tracker._dist_matrix(A, B)

        # Check shape
        assert distances.shape == (2, 2)

        # Check some expected values (approximately)
        assert abs(distances[0, 0] - 0.0) < 0.1  # Same point
        assert abs(distances[1, 1] - 7.07) < 0.1  # sqrt(5^2 + 5^2) ≈ 7.07

    def test_multiple_new_objects(self):
        """Test adding multiple new objects simultaneously"""
        detections = [(10, 10, 8), (50, 50, 10), (100, 100, 12)]

        result = self.tracker.update(detections)

        assert len(result) == 3
        assert set(result.keys()) == {1, 2, 3}

    def test_partial_object_loss(self):
        """Test when some objects disappear but others remain"""
        # Add three objects
        self.tracker.update([(10, 10, 8), (50, 50, 10), (100, 100, 12)])

        # Next frame: only detect two objects (middle one missing)
        result = self.tracker.update([(12, 12, 8), (102, 102, 12)])

        # Should have 3 objects total (2 active, 1 disappeared)
        assert len(result) == 3

        # Two objects should be active (disappeared count = 0)
        active_count = len(
            [obj_id for obj_id in result if self.tracker.disappeared[obj_id] == 0]
        )
        assert active_count == 2

        # One object should be marked as disappeared
        disappeared_count = len(
            [obj_id for obj_id in result if self.tracker.disappeared[obj_id] > 0]
        )
        assert disappeared_count == 1

        # The middle object (ID 2) should be the one that disappeared
        assert self.tracker.disappeared[2] == 1
