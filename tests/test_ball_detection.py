"""
Tests for PoolMind ball detection functionality
"""
from unittest.mock import Mock, patch

import numpy as np
import pytest

from poolmind.detect.balls import BallDetector


class TestBallDetector:
    """Test cases for BallDetector class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.config = {
            "hough_dp": 1.2,
            "hough_min_dist": 16,
            "hough_param1": 100,
            "hough_param2": 30,
            "ball_min_radius": 8,
            "ball_max_radius": 18,
        }
        self.detector = BallDetector(self.config)

    def test_detector_initialization(self):
        """Test detector initializes with correct parameters"""
        assert self.detector.hough_dp == 1.2
        assert self.detector.hough_min_dist == 16
        assert self.detector.hough_param1 == 100
        assert self.detector.hough_param2 == 30
        assert self.detector.ball_min_radius == 8
        assert self.detector.ball_max_radius == 18

    def test_detector_with_default_config(self):
        """Test detector works with empty config (default values)"""
        detector = BallDetector({})
        assert detector.hough_dp == 1.2  # default value
        assert detector.hough_min_dist == 16  # default value

    @patch("poolmind.detect.balls.cv2")
    def test_detect_no_circles(self, mock_cv2):
        """Test detection when no circles are found"""
        # Mock OpenCV functions
        mock_cv2.cvtColor.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_cv2.GaussianBlur.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_cv2.HoughCircles.return_value = None

        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Run detection
        result = self.detector.detect(test_image)

        # Should return empty list
        assert result == []

    @patch("poolmind.detect.balls.cv2")
    def test_detect_with_circles(self, mock_cv2):
        """Test detection when circles are found"""
        # Mock OpenCV functions
        mock_cv2.cvtColor.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_cv2.GaussianBlur.return_value = np.zeros((100, 100), dtype=np.uint8)

        # Mock circle detection result
        circles = np.array([[[50, 50, 10], [30, 30, 8]]], dtype=np.float32)
        mock_cv2.HoughCircles.return_value = circles

        # Create test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)

        # Mock color classification
        with patch.object(self.detector, "_classify_ball_color", return_value="solid"):
            result = self.detector.detect(test_image)

        # Should return list with detected balls
        assert len(result) == 2
        assert result[0] == (50, 50, 10, "solid")
        assert result[1] == (30, 30, 8, "solid")

    def test_classify_ball_color_cue(self):
        """Test cue ball classification (high brightness, low saturation)"""
        # Create white image (cue ball)
        white_image = np.full((20, 20, 3), 255, dtype=np.uint8)

        with patch("poolmind.detect.balls.cv2") as mock_cv2:
            mock_cv2.cvtColor.return_value = np.zeros((20, 20, 3), dtype=np.uint8)
            mock_cv2.mean.return_value = (180, 30, 220, 0)  # Low H, low S, high V

            result = self.detector._classify_ball_color(white_image, 10, 10, 5)

            assert result == "cue"

    def test_classify_ball_color_solid(self):
        """Test solid ball classification (high saturation, red/yellow range)"""
        test_image = np.zeros((20, 20, 3), dtype=np.uint8)

        with patch("poolmind.detect.balls.cv2") as mock_cv2:
            mock_cv2.cvtColor.return_value = np.zeros((20, 20, 3), dtype=np.uint8)
            mock_cv2.mean.return_value = (20, 150, 180, 0)  # Red range, high S

            result = self.detector._classify_ball_color(test_image, 10, 10, 5)

            assert result == "solid"

    def test_classify_ball_color_stripe(self):
        """Test stripe ball classification (high saturation, other colors)"""
        test_image = np.zeros((20, 20, 3), dtype=np.uint8)

        with patch("poolmind.detect.balls.cv2") as mock_cv2:
            mock_cv2.cvtColor.return_value = np.zeros((20, 20, 3), dtype=np.uint8)
            mock_cv2.mean.return_value = (100, 150, 180, 0)  # Blue range, high S

            result = self.detector._classify_ball_color(test_image, 10, 10, 5)

            assert result == "stripe"

    def test_classify_ball_color_unknown(self):
        """Test unknown ball classification (low saturation)"""
        test_image = np.zeros((20, 20, 3), dtype=np.uint8)

        with patch("poolmind.detect.balls.cv2") as mock_cv2:
            mock_cv2.cvtColor.return_value = np.zeros((20, 20, 3), dtype=np.uint8)
            mock_cv2.mean.return_value = (100, 50, 180, 0)  # Low saturation

            result = self.detector._classify_ball_color(test_image, 10, 10, 5)

            assert result == "unknown"

    def test_classify_ball_color_empty_roi(self):
        """Test classification with empty ROI"""
        test_image = np.zeros((10, 10, 3), dtype=np.uint8)

        # ROI outside image bounds
        result = self.detector._classify_ball_color(test_image, 50, 50, 5)

        assert result == "unknown"
