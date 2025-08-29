"""
Tests for PoolMind ArUco marker detection and calibration
"""
from unittest.mock import patch

import numpy as np
import pytest

from poolmind.calib.markers import MarkerHomography


class TestMarkerHomography:
    """Test cases for MarkerHomography class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = {
            "corner_ids": [0, 1, 2, 3],
            "table_w": 2000,
            "table_h": 1000,
            "ema_alpha": 0.3,
        }

    def test_marker_homography_initialization(self):
        """Test MarkerHomography initializes correctly"""
        homography = MarkerHomography(self.config)

        assert homography.corner_ids == [0, 1, 2, 3]
        assert homography.table_w == 2000
        assert homography.table_h == 1000
        assert abs(homography.alpha - 0.3) < 1e-6
        assert homography.H is None
        assert homography.H_inv is None

        # Check destination points
        expected_dst = np.array(
            [[0, 0], [1999, 0], [1999, 999], [0, 999]], dtype=np.float32
        )
        np.testing.assert_array_equal(homography._dst_pts, expected_dst)

    def test_marker_homography_default_config(self):
        """Test MarkerHomography with default configuration"""
        homography = MarkerHomography({})

        assert homography.corner_ids == [0, 1, 2, 3]
        assert homography.table_w == 2000
        assert homography.table_h == 1000
        assert abs(homography.alpha - 0.2) < 1e-6

    @patch("poolmind.calib.markers._ARUCO_AVAILABLE", False)
    def test_homography_from_frame_no_aruco_available(self):
        """Test homography calculation when ArUco is not available"""
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        homography = MarkerHomography(self.config)
        result_h, result_h_inv, debug = homography.homography_from_frame(test_frame)

        assert result_h is None
        assert result_h_inv is None
        assert debug is None

    def test_ema_homography_smoothing(self):
        """Test EMA smoothing of homography matrices"""
        homography = MarkerHomography(self.config)

        # Create test homography matrices
        h_prev = np.array(
            [[1.0, 0.0, 10.0], [0.0, 1.0, 20.0], [0.0, 0.0, 1.0]], dtype=np.float32
        )

        h_new = np.array(
            [[1.1, 0.1, 15.0], [0.1, 1.1, 25.0], [0.0, 0.0, 1.0]], dtype=np.float32
        )

        alpha = 0.3
        result = homography._ema_H(h_prev, h_new, alpha)

        # Expected result: (1-alpha) * h_prev + alpha * h_new
        expected = 0.7 * h_prev + 0.3 * h_new

        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_custom_corner_ids(self):
        """Test MarkerHomography with custom corner IDs"""
        config = {
            "corner_ids": [10, 11, 12, 13],
            "table_w": 1500,
            "table_h": 800,
            "ema_alpha": 0.5,
        }

        homography = MarkerHomography(config)

        assert homography.corner_ids == [10, 11, 12, 13]
        assert homography.table_w == 1500
        assert homography.table_h == 800
        assert abs(homography.alpha - 0.5) < 1e-6

    def test_empty_corner_ids(self):
        """Test MarkerHomography with empty corner IDs"""
        config = {"corner_ids": []}

        homography = MarkerHomography(config)
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        result_h, result_h_inv, debug = homography.homography_from_frame(test_frame)

        assert result_h is None
        assert result_h_inv is None
        assert debug is None
