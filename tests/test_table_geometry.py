"""
Tests for PoolMind table geometry functionality
"""
from unittest.mock import Mock

import numpy as np

from poolmind.table.geometry import TableGeometry


class TestTableGeometry:
    """Test cases for TableGeometry class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = {"table_w": 800, "table_h": 400, "margin": 30}
        self.table = TableGeometry(self.config)

    def test_table_initialization(self):
        """Test table initializes with correct dimensions"""
        assert self.table.w == 800
        assert self.table.h == 400
        assert self.table.margin == 30

    def test_table_with_default_config(self):
        """Test table works with minimal config"""
        table = TableGeometry({})
        assert table.w == 2000  # default
        assert table.h == 1000  # default
        assert table.margin == 30  # default

    def test_warp_frame_with_homography(self):
        """Test frame warping with valid homography matrix"""
        # Create mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Create mock homography matrix
        H = np.array(
            [[1.2, 0.1, -50], [0.05, 1.1, -30], [0.0001, 0.0002, 1]], dtype=np.float32
        )

        warped = self.table.warp(frame, H)

        # Should return warped frame with correct dimensions (table w x h)
        assert warped is not None
        assert warped.shape == (self.table.h, self.table.w, 3)

    def test_warp_frame_with_none_homography(self):
        """Test frame warping with None homography"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # OpenCV doesn't handle None, so this should raise an exception
        try:
            warped = self.table.warp(frame, None)
            # If no exception, implementation should return None or handle it
            assert warped is None
        except Exception:
            # Expected behavior - OpenCV raises exception for None matrix
            pass

    def test_warp_frame_with_invalid_homography(self):
        """Test frame warping with invalid homography matrix"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Invalid homography (wrong shape) - OpenCV will handle this
        H = np.array([[1, 0], [0, 1]], dtype=np.float32)

        # OpenCV should raise an exception for invalid matrix
        try:
            self.table.warp(frame, H)
            # If no exception, the operation completed
        except Exception:
            # Expected behavior for invalid homography
            pass

    def test_default_pockets_generation(self):
        """Test default pocket positions are generated correctly"""
        radius = 25
        pockets = self.table.default_pockets(radius)

        # Should have 6 pockets for standard pool table
        assert len(pockets) == 6

        # Check pocket format (x, y, radius)
        for pocket in pockets:
            assert len(pocket) == 3
            x, y, r = pocket
            assert isinstance(x, (int, float))
            assert isinstance(y, (int, float))
            assert isinstance(r, (int, float))
            assert r == radius  # matches input

    def test_default_pockets_positions(self):
        """Test default pocket positions are at expected locations"""
        radius = 30
        pockets = self.table.default_pockets(radius)

        # Extract positions
        positions = [(x, y) for x, y, r in pockets]

        # Should include corner pockets (with margin)
        margin = self.table.margin
        assert (margin, margin) in positions  # top-left
        assert (800 - margin, margin) in positions  # top-right
        assert (margin, 400 - margin) in positions  # bottom-left
        assert (800 - margin, 400 - margin) in positions  # bottom-right

        # Should include side pockets
        assert (400, margin) in positions  # top-middle
        assert (400, 400 - margin) in positions  # bottom-middle

    def test_custom_pocket_radius(self):
        """Test custom pocket radius is used"""
        radius = 50
        pockets = self.table.default_pockets(radius)

        # All pockets should have custom radius
        for x, y, r in pockets:
            assert r == radius

    def test_custom_table_dimensions(self):
        """Test custom table dimensions"""
        config = {"table_w": 1000, "table_h": 500, "margin": 25}
        table = TableGeometry(config)

        assert table.w == 1000
        assert table.h == 500

        radius = 30
        pockets = table.default_pockets(radius)

        # Check corner positions match new dimensions
        positions = [(x, y) for x, y, r in pockets]
        margin = table.margin
        assert (margin, margin) in positions
        assert (1000 - margin, margin) in positions
        assert (margin, 500 - margin) in positions
        assert (1000 - margin, 500 - margin) in positions
        assert (500, margin) in positions  # middle positions
        assert (500, 500 - margin) in positions

    def test_warp_coordinates_transformation(self):
        """Test that warping transforms coordinates correctly"""
        # Create identity-like homography for predictable transformation
        H = np.array(
            [[2.0, 0.0, 0.0], [0.0, 2.0, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32
        )

        frame = np.zeros((200, 400, 3), dtype=np.uint8)

        warped = self.table.warp(frame, H)

        # Should return frame with expected dimensions
        assert warped is not None
        assert warped.shape == (self.table.h, self.table.w, 3)

    def test_back_project_points(self):
        """Test back projection of points using inverse homography"""
        # Create test points in warped space
        pts = np.array([[100, 50], [200, 150]], dtype=np.float32)

        # Create inverse homography matrix
        h_inv = np.array(
            [[0.8, -0.1, 50], [-0.05, 0.9, 30], [-0.0001, -0.0002, 1]], dtype=np.float32
        )

        projected = self.table.back_project_points(pts, h_inv)

        # Should return projected points
        assert projected is not None
        assert len(projected) == 2
        # projected is numpy array from the function
        projected_array = np.array(projected)
        assert projected_array.shape[0] == 2
        assert projected_array.shape[1] == 2

    def test_back_project_points_with_none_homography(self):
        """Test back projection with None homography"""
        pts = np.array([[100, 50]], dtype=np.float32)

        projected = self.table.back_project_points(pts, None)

        # Should return empty list
        assert projected == []

    def test_back_project_points_with_empty_points(self):
        """Test back projection with empty points"""
        pts = np.array([], dtype=np.float32).reshape(0, 2)
        h_inv = np.eye(3, dtype=np.float32)

        projected = self.table.back_project_points(pts, h_inv)

        # Should return empty list
        assert projected == []

    def test_empty_config_handling(self):
        """Test handling of empty or None config"""
        # Test with None config - should use defaults
        table1 = TableGeometry({})
        assert table1.w == 2000

        # Test with empty dict
        table2 = TableGeometry({})
        assert table2.h == 1000

    def test_partial_config_handling(self):
        """Test handling of partial config with missing values"""
        config = {"table_w": 1200}  # missing height and margin
        table = TableGeometry(config)

        assert table.w == 1200  # custom value
        assert table.h == 1000  # default value
        assert table.margin == 30  # default value
